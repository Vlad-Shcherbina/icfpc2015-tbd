#include "placement.h"

#include <algorithm>
#include <iostream>
#include <map>
#include <stack>

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
    index = 0;

    v_index = vector<int>(graph.GetSize(), UNDEFINED);
    lowlink = vector<int>(graph.GetSize(), UNDEFINED);
    onstack = vector<bool>(graph.GetSize(), false);

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


class DpSolver {
public:
  const DFA &dfa;
  const Graph &graph;

  DpSolver(const DFA &dfa, const Graph &graph) : dfa(dfa), graph(graph) {

  }

  vector<int> GetResult() const {
    return {42};
  }
};


std::vector<int> DFA::FindBestPath(const Graph &graph, int destination) const {
  return DpSolver(*this, graph).GetResult();
}
