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

 private:
  std::vector<std::array<int, 6> > tr;
  std::vector<Placement> meaning;
  int start_node;
};
