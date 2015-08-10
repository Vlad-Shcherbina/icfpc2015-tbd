#include "placement.h"

#include <algorithm>
#include <iostream>
#include <map>
#include <unordered_map>
#include <stack>
#include <memory>

using namespace std;

Unit UnitBuilder::Build(int board_width, int board_height) {
  Unit unit;
  for (const auto& pos_and_shape : shapes_) {
    const auto& pos = pos_and_shape.first;
    const auto& shape = pos_and_shape.second;

    int offset_x = shape.min_x;
    int begin_pos_x = shape.min_x - offset_x;
    int end_pos_x = board_width + shape.min_x - shape.max_x;
    int pivot_x = std::get<0>(pos) - offset_x;

    assert(begin_pos_x >= 0);
    assert(end_pos_x >= 0);
    assert(begin_pos_x < board_width);
    assert(end_pos_x <= board_width);

    int offset_y = shape.min_y & -2;
    int begin_pos_y = shape.min_y - offset_y;
    int end_pos_y = board_height + shape.min_y - shape.max_y;
    int pivot_y = std::get<1>(pos) - offset_y;

    assert(begin_pos_y >= 0);
    assert(end_pos_y >= 0);
    assert(begin_pos_y < board_height);
    assert(end_pos_y <= board_height);

    int angle = std::get<2>(pos);

    for (int i = 0; i < shape.mask.size(); ++i) {
      const auto& row_mask = shape.mask[i];
      for (int j = 0; j < row_mask.size() + 1; ++j) {
        for (int dx = 0; dx < 64; ++dx) {
          Unit::ShapeSegment segment;

          if (j < row_mask.size()) segment.mask |= row_mask[j] << dx;
          if (j > 0 && dx > 0) segment.mask |= row_mask[j - 1] >> (64 - dx);

          if (segment.mask == 0) continue;

          segment.begin_pos_x = (begin_pos_x - dx + 63) / 64 + j;
          segment.end_pos_x = (end_pos_x - dx + 63) / 64 + j;
          segment.pivot_dx = pivot_x + dx - 64 * segment.begin_pos_x;

          if (segment.end_pos_x <= segment.begin_pos_x) continue;

          assert(segment.begin_pos_x >= 0);
          assert(segment.end_pos_x >= 0);
          assert(segment.begin_pos_x < (board_width + 63) / 64);
          assert(segment.end_pos_x <= (board_width + 63) / 64);

          segment.begin_pos_y = begin_pos_y + i;
          segment.end_pos_y = end_pos_y + i;
          segment.pivot_dy = pivot_y - segment.begin_pos_y;

          assert(segment.begin_pos_y >= 0);
          assert(segment.end_pos_y >= 0);
          assert(segment.begin_pos_y < board_height);
          assert(segment.end_pos_y <= board_height);

          segment.angle = angle;
          unit.num_angles = std::max(unit.num_angles, angle + 1);

          unit.segments.push_back(segment);
        }
      }
    }
  }
  return unit;
}

void UnitBuilder::Shape::SetCell(
    int min_x, int min_y,
    int max_x, int max_y,
    int cell_x, int cell_y) {
  assert(min_x <= max_x);
  assert(min_y <= max_y);
  assert(min_x <= cell_x);
  assert(min_y <= cell_y);
  assert(cell_x <= max_x);
  assert(cell_y <= max_y);

  if (mask.empty()) {
    mask.resize(max_y - min_y + 1);
    this->min_x = min_x;
    this->min_y = min_y;
    this->max_x = max_x;
    this->max_y = max_y;
  } else {
    assert(mask.size() == max_y - min_y + 1);
    assert(this->min_x == min_x);
    assert(this->min_y == min_y);
    assert(this->max_x == max_x);
    assert(this->max_y == max_y);
  }
  auto& row_mask = mask[cell_y - min_y];
  if (row_mask.empty()) {
    row_mask.resize((max_x - min_x + 64) / 64);
  } else {
    assert(row_mask.size() == (max_x - min_x + 64) / 64);
  }
  row_mask[(cell_x - min_x) / 64] |= 1ULL << ((cell_x - min_x) % 64);
}

void GraphBuilder::ComputeValidPlacements() {
  assert(current_unit_ != nullptr);
  for (const auto& segment : current_unit_->segments) {
    for (int y = segment.begin_pos_y; y < segment.end_pos_y; y += 2) {
      for (int x = segment.begin_pos_x; x < segment.end_pos_x; ++x) {
        auto pos = std::make_tuple(
            segment.pivot_dx + x * 64,
            segment.pivot_dy + y,
            segment.angle);

        assert(y < board_.size());
        assert(x < board_[y].size());

        is_invalid_pos_[pos] |= board_[y][x] & segment.mask;
      }
    }
  }
}

Graph GraphBuilder::Build(int pivot_x, int pivot_y, int angle) {
  assert(current_unit_ != nullptr);
  assert(!is_invalid_pos_.empty());

  int num_angles = current_unit_->num_angles;

  std::stack<std::tuple<int, int, int> > stack;
  std::map<std::tuple<int, int, int>, int> labels;
  std::vector<std::array<int, 6> > tr;

  auto start_node = std::make_tuple(pivot_x, pivot_y, angle);
  stack.push(start_node);
  labels[start_node] = 0;
  tr.push_back({});

  while (!stack.empty()) {
    auto src = stack.top();
    stack.pop();

    int src_label = labels[src];

    for (int i = 0; i < 6; ++i) {
      auto dst = src;
      switch (i) {
        case Graph::W:
          std::get<0>(dst) -= 1;
          break;
        case Graph::E:
          std::get<0>(dst) += 1;
          break;
        case Graph::SW:
          std::get<0>(dst) += (std::get<1>(dst) & 1) - 1;
          std::get<1>(dst) += 1;
          break;
        case Graph::SE:
          std::get<0>(dst) += (std::get<1>(dst) & 1);
          std::get<1>(dst) += 1;
          break;
        case Graph::CW:
          std::get<2>(dst) = (std::get<2>(dst) + 1) % num_angles;
          break;
        case Graph::CCW:
          std::get<2>(dst) = (std::get<2>(dst) + num_angles - 1) % num_angles;
          break;
        default:
          assert(false);
      }
      assert(std::get<2>(dst) < 6);
      if (IsValidPlacement(dst)) {
        int dst_label = labels.insert({dst, tr.size()}).first->second;
        if (dst_label == tr.size()) {
          tr.push_back({});
          stack.push(dst);
        }
        tr[src_label][i] = dst_label;
      } else {
        tr[src_label][i] = Graph::COLLISION;
      }
    }
    assert(labels.size() == tr.size());
  }
  Graph graph;
  graph.tr.swap(tr);
  graph.meaning.resize(graph.tr.size());
  graph.start_node = 0;

  for (const auto& pos_and_label : labels) {
    const auto& pos = pos_and_label.first;
    const auto& label = pos_and_label.second;
    assert(label < graph.meaning.size());
    graph.meaning[label].x = std::get<0>(pos);
    graph.meaning[label].y = std::get<1>(pos);
    graph.meaning[label].angle = std::get<2>(pos);
  }

  return graph;
}

// https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
class TarjanSCC {
public:
  const Graph &graph;
  vector<vector<int> > result;

  int index;
  vector<int> v_index;
  vector<int> lowlink;
  vector<bool> onstack;

  vector<int> S;

  const int UNDEFINED = -42;

  TarjanSCC(const Graph &graph) : graph(graph) {
    v_index = vector<int>(graph.GetSize(), UNDEFINED);
    lowlink = vector<int>(graph.GetSize(), UNDEFINED);
    onstack = vector<bool>(graph.GetSize(), false);

    index = 0;
    S.clear();

    for (int v = 0; v < v_index.size(); v++) {
      if (v_index[v] == UNDEFINED)
        StrongConnect(v);
    }

    reverse(result.begin(), result.end());
  }

  void StrongConnect(int v) {
    assert(v >= 0);
    assert(v < graph.GetSize());

    v_index[v] = index;
    lowlink[v] = index;
    index++;
    S.push_back(v);
    onstack[v] = true;

    for (int i = 0; i < 6; i++) {
      int w = graph.tr[v][i];
      if (w == Graph::COLLISION)
        continue;
      if (v_index.at(w) == UNDEFINED) {
        StrongConnect(w);
        lowlink[v] = min(lowlink[v], lowlink[w]);
      } else if (onstack[w]) {
        lowlink[v] = min(lowlink[v], v_index[w]);
      }
    }

    if (lowlink[v] == v_index[v]) {
      result.emplace_back();
      int w;
      do {
        assert(!S.empty());
        w = S.back();
        S.pop_back();
        onstack[w] = false;
        result.back().push_back(w);
      } while (w != v);
    }
  }

  vector<vector<int> > GetResult() const {
    return result;
  }
};


std::vector<std::vector<int> > StronglyConnectedComponents(const Graph &graph) {
  return TarjanSCC(graph).GetResult();
}



// Linked lists that share a lot of tails.
struct Fragment {
  int ch;
  shared_ptr<Fragment> prev;
};
typedef shared_ptr<Fragment> Chain;


Chain EmptyChain() {
  return nullptr;
}

Chain AppendToChain(Chain c, int ch) {
  Chain result(new Fragment);
  result->ch = ch;
  result->prev = c;
  return result;
}

vector<int> ChainToVector(Chain c) {
  vector<int> result;
  while (c != nullptr) {
    result.push_back(c->ch);
    c = c->prev;
  }
  reverse(result.begin(), result.end());
  return result;
}


const int NEG_INF = -1000000000;

struct Status {

  int score;
  Chain best;

  void Merge(const Status &other) {
    if (other.score > score)
      *this = other;
  }

  Status Translate(int cmd) const {
    if (score == NEG_INF) return *this;
    Status s = *this;
    s.score--;
    s.best = AppendToChain(best, cmd * 6);
    return s;
  }
};


template<typename T>
std::ostream& operator<<(std::ostream &out, const std::vector<T> &v) {
  out << "[";
  bool first = true;
  for (const auto &e : v) {
    if (!first)
      out << ", ";
    first = false;
    out << e;
  }
  out << "]";
  return out;
}
template<typename T1, typename T2>
std::ostream& operator<<(std::ostream &out, const std::pair<T1, T2> &p) {
  out << "(" << p.first << ", " << p.second << ")";
  return out;
}


class DSU {
public:
  unordered_map<int, int> up;
  unordered_map<int, int> rank;

  DSU(const vector<int>& items) {
    for (int i : items) {
      assert(up.count(i) == 0);
      up[i] = i;
      rank[i] = 0;
    }
  }

  int Find(int x) {
    if (up.at(x) != x) {
      up.at(x) = Find(up.at(x));
    }
    return up.at(x);
  }

  void Union(int x, int y) {
    int x_root = Find(x);
    int y_root = Find(y);

    assert(x_root != y_root);

    if (rank.at(x_root) < rank.at(y_root)) {
      up.at(x_root) = y_root;
    } else if (rank.at(x_root) > rank.at(y_root)) {
      up.at(y_root) = x_root;
    } else {
      up.at(y_root) = x_root;
      rank.at(x_root)++;
    }
  }
};


class DpSolver {
public:
  const DFA &dfa;
  const Graph &graph;

  vector<Status> statii;

  vector<int> scc_by_node;

  void ShowNode(int node) {
    auto m = graph.meaning.at(node);
    cout << "(x=" << m.x << ", y=" << m.y << ", a=" << m.angle << ")";
  }
  void ShowNodes(vector<int> nodes) {
    cout << "[";
    for (int node : nodes) {
      ShowNode(node);
      cout << ", ";
    }
    cout << "]" << endl;
  }

  DpSolver(const DFA &dfa, const Graph &graph) : dfa(dfa), graph(graph) {
    statii = {(size_t) graph.GetSize(), MakeInvalidStatus()};
    statii.at(graph.GetStartNode()) = MakeInitialStatus();

    scc_by_node = vector<int>(graph.GetSize(), 0);

    auto sccs = StronglyConnectedComponents(graph);
    int i = 0;
    for (const auto &scc : sccs) {
      for (int node : scc)
        scc_by_node[node] = i;
      i++;
    }

    // cout << scc_by_node << endl;

    //cout << sccs << endl;
    // for (auto scc : sccs) {
    //   ShowNodes(scc);
    // }

    for (const auto &scc : sccs) {
      UpdateSCC(scc);
      for (int node : scc) {
        for (int cmd = 0; cmd < 6; cmd++) {
          int node2 = graph.tr[node][cmd];
          if (node2 == Graph::COLLISION)
            continue;

          if (scc_by_node.at(node2) > scc_by_node.at(node)) {
            //cout << node << " -> " << node2 << endl;
            statii[node2].Merge(statii[node].Translate(cmd));
            //
          }
        }
      }
    }

    // for (const auto &scc : sccs) {
    //   cout << "---" << endl;
    //   for (int node : scc) {
    //     cout << node << " " << statii[node].score << " " << ChainToVector(statii[node].best) << endl;
    //   }
    // }
  }

  typedef pair<int, int> Arrow;  // (node, cmd)
  unordered_map<int, vector<Arrow>> incoming_arrows;
  map<Arrow, Status> status_by_arrow;

  int ArrowEnd(const Arrow &a) {
    int node = graph.tr[a.first][a.second];
    assert(node >= 0);
    assert(node < graph.GetSize());
    return node;
  }

  void UpdateSCC(const vector<int> &scc) {
    assert(!scc.empty());

    vector<Arrow> spanning_tree;

    DSU dsu(scc);

    // TODO: actual spanning tree
    // cout << "SCC: " << scc << endl;

    for (int node : scc) {
      for (int cmd = 0; cmd < 6; cmd++) {
        int node2 = graph.tr[node][cmd];
        if (node2 == Graph::COLLISION)
          continue;
        if (scc_by_node.at(node) != scc_by_node.at(node2))
          continue;
        if (node2 == node)
          continue;

        // cout << "node " << node << ";  node2 " << node2 << endl;

        if (dsu.Find(node) != dsu.Find(node2)) {
          //UniteIslands(scc, node, node2);
          dsu.Union(node, node2);
          spanning_tree.emplace_back(node, cmd);
          int rev_cmd = Graph::ReverseCommand((Graph::Command)cmd);
          // cout << cmd << " " << rev_cmd << endl;
          assert(graph.tr[node2][rev_cmd] == node);
          spanning_tree.emplace_back(node2, rev_cmd);
        }
        //spanning_tree.emplace_back(node, cmd);
      }
    }

    // Check that all islands are united.
    for (int node : scc)
      assert(dsu.Find(node) == dsu.Find(scc.front()));

    // cout << "Updating SCC " << scc << endl;
    // cout << "Spanning tree: " << spanning_tree << endl;

    incoming_arrows.clear();
    for (Arrow arrow : spanning_tree) {
      incoming_arrows[ArrowEnd(arrow)].push_back(arrow);
    }

    status_by_arrow.clear();
    for (Arrow arrow : spanning_tree) {
      UpdateArrow(arrow);
    }

    ApplyStatusByArrow();
  }

  void UpdateArrow(const Arrow &a) {
    if (status_by_arrow.count(a) > 0)
      return;

    int node2 = ArrowEnd(a);

    Status status = statii.at(a.first);

    bool found_reverse = false;
    for (const auto &ia : incoming_arrows.at(a.first)) {
      assert(ArrowEnd(ia) == a.first);
      //cout << "  ia " << ia << " " << ArrowEnd(ia) << endl;
      if (ia.first == node2) {
        found_reverse = true;
        continue;
      }
      UpdateArrow(ia);
      status.Merge(status_by_arrow.at(ia));
    }
    // cout << "UA " << a << " " << node2 << endl;

    assert(!incoming_arrows.at(a.first).empty());  // todo: remove in non-tree case
    if (!incoming_arrows.at(a.first).empty())
      assert(found_reverse);

    status_by_arrow[a] = status.Translate(a.second);
  }

  void ApplyStatusByArrow() {
    for (const auto &kv : status_by_arrow) {
      const Arrow &a = kv.first;
      int node2 = ArrowEnd(a);
      statii.at(node2).Merge(kv.second);
    }
  }


  Status MakeInitialStatus() const {
    Status status;
    status.score = 0;
    status.best = EmptyChain();
    return status;
  }

  Status MakeInvalidStatus() const {
    Status status;
    status.score = NEG_INF;
    status.best = EmptyChain();
    return status;
  }

  vector<int> GetResult(int destination) const {
    /*Chain c = EmptyChain();
    c = AppendToChain(c, 1);
    c = AppendToChain(c, 2);
    c = AppendToChain(c, 3);
    return ChainToVector(c);*/

    auto status = statii.at(destination);
    assert(status.score != NEG_INF);

    return ChainToVector(status.best);

    //return {42};
  }
};


std::vector<int> DFA::FindBestPath(const Graph &graph, int destination) const {
  return DpSolver(*this, graph).GetResult(destination);
}
