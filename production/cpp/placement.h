#pragma once

#include <cassert>
#include <array>
#include <vector>


struct Graph {
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

  std::vector<std::array<int, 6> > tr;
  std::vector<Placement> meaning;
  int start_node;
};


std::vector<std::vector<int> > StronglyConnectedComponents(const Graph &graph);


class DFA {
public:
  std::vector<int> FindBestPath(const Graph &graph) const {
    return {};
  }
};
