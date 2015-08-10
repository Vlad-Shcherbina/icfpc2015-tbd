#pragma once

#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <vector>

struct Graph {
  Graph() {}
  Graph(int size) : tr(size), meaning(size) {}

  // Order should be in sync with INDEXED_ACTIONS in big_step_game.py!
  enum Command {
    W = 0,
    E = 1,
    SW = 2,
    SE = 3,
    CW = 4,
    CCW = 5,
  };

  static Command ReverseCommand(Command c) {
    switch (c) {
      case W: return E;
      case E: return W;

      case CW: return CCW;
      case CCW: return CW;

      default: assert(false);
    }
  }

  enum EndState {
    COLLISION = -1,
    UNINTERESTING = -2,
  };

  struct Placement {
    int x;
    int y;
    int angle;
  };

  int GetSize() const {
    assert(tr.size() == meaning.size());
    return tr.size();
  }

  void SetStartNode(int x) { start_node = x; }
  int GetStartNode() const { return start_node; }

  void SetNext(int src, Command command, int dst) { tr[src][command] = dst; }
  int GetNext(int src, Command command) const { return tr[src][command]; }

  void SetNodeMeaning(int node, int x, int y, int angle) {
    meaning[node].x = x;
    meaning[node].y = y;
    meaning[node].angle = angle;
  }

  int GetNodeMeaningX(int node) const {
    return meaning[node].x;
  }
  int GetNodeMeaningY(int node) const {
    return meaning[node].y;
  }
  int GetNodeMeaningAngle(int node) const {
    return meaning[node].angle;
  }

  int FindNodeByMeaning(int x, int y, int angle) const {
    for (int i = 0; i < meaning.size(); i++) {
      if (meaning[i].x == x && meaning[i].y == y && meaning[i].angle == angle)
        return i;
    }
    return -1;
  }

  // Return list of all nodes that immediately precede state COLLISION, and
  // that are reachable from initial node.
  // We don't check reachability here because it's enforced by graph
  // construction process.
  std::vector<int> GetLockedNodes() const {
    std::vector<int> result;
    for (int i = 0; i < tr.size(); i++) {
      for (int j = 0; j < 6; j++) {
        if (tr[i][j] == COLLISION) {
          result.push_back(i);
          break;
        }
        assert(tr[i][j] >= 0 && tr[i][j] < tr.size());
      }
    }
    return result;
  }

  // Add new node. Its transitions are looped to itself.
  // Return its index.
  int AddNewNode() {
    int node = tr.size();

    tr.emplace_back();
    for (int i = 0; i < 6; i++)
      tr[node][i] = node;

    meaning.emplace_back();
    meaning.back().x = -1;
    meaning.back().y = -1;
    meaning.back().angle = -1; // this angle is intentionally impossible

    return node;
  }

  void Append(const Graph& graph) {
    if (tr.empty()) {
      tr = graph.tr;
      meaning = graph.meaning;
      start_node = graph.start_node;
    } else {
      assert(graph.start_node == 0);

      tr.pop_back();
      meaning.pop_back();

      int offset = tr.size();
      for (auto edges : graph.tr) {
        for (int& node : edges) {
          if (node >= 0) node += offset;
        }
        tr.emplace_back(std::move(edges));
      }
      meaning.insert(meaning.end(), graph.meaning.begin(), graph.meaning.end());

      assert(tr.size() == meaning.size());
    }
  }

  std::vector<std::array<int, 6> > tr;
  std::vector<Placement> meaning;
  int start_node;
};

inline bool operator==(const Graph::Placement& a, const Graph::Placement& b) {
  return a.x == b.x && a.y == b.y && a.angle == b.angle;
}

inline bool IsIdentical(const Graph& a, const Graph& b) {
  return
      a.tr == b.tr &&
      a.meaning == b.meaning &&
      a.start_node == b.start_node;
}

struct Unit {
  Unit() : num_angles(0) {}

  struct ShapeSegment {
    ShapeSegment() : mask(0) {}

    uint64_t mask;

    int pivot_dx;
    int pivot_dy;
    int angle;

    int begin_pos_x, end_pos_x;
    int begin_pos_y, end_pos_y;
  };

  std::vector<ShapeSegment> segments;
  int num_angles;
};

class UnitBuilder {
 public:
  void SetCell(
      int pivot_x, int pivot_y, int angle,
      int min_x, int min_y,
      int max_x, int max_y,
      int cell_x, int cell_y) {
    shapes_[std::make_tuple(pivot_x, pivot_y, angle)].SetCell(
        min_x, min_y, max_x, max_y, cell_x, cell_y);
  }

  Unit Build(int board_width, int board_height);

 private:
  struct Shape {
    void SetCell(
        int min_x, int min_y,
        int max_x, int max_y,
        int cell_x, int cell_y);

    std::vector<std::vector<uint64_t> > mask;
    int min_x, min_y, max_x, max_y;
  };

  std::map<std::tuple<int, int, int>, Shape> shapes_;
};

class GraphBuilder {
 public:
  GraphBuilder(int board_width, int board_height)
      : board_(board_height, std::vector<uint64_t>((board_width + 63) / 64)) {}

  void FillCell(int x, int y) {
    // Least significant bit is bit 0.
    board_[y][x / 64] |= 1ULL << (x % 64);
    is_invalid_pos_.clear();
  }

  void SetCurrentUnit(const Unit* unit) {
    current_unit_ = unit;
    is_invalid_pos_.clear();
  }

  void ComputeValidPlacements();
  Graph Build(int pivot_x, int pivot_y, int angle);

  bool IsValidPlacement(int pivot_x, int pivot_y, int angle) const {
    return IsValidPlacement(std::make_tuple(pivot_x, pivot_y, angle));
  }

 private:
  bool IsValidPlacement(const std::tuple<int, int, int>& pos) const {
    auto it = is_invalid_pos_.find(pos);
    return it != is_invalid_pos_.end() && it->second == false;
  }

  const Unit* current_unit_;
  std::vector<std::vector<uint64_t> > board_;
  std::map<std::tuple<int, int, int>, bool> is_invalid_pos_;
};

std::vector<std::vector<int> > StronglyConnectedComponents(const Graph &graph);

class DFA {
public:
  std::vector<int> FindBestPath(const Graph &graph, int destination) const;
};
