#pragma once

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
    LOCKED = -1,
    UNINTERESTING = -2,
  };

  struct Placement {
    int x;
    int y;
    int angle;
  };

  void SetNext(int src, Command command, int dst) { tr[src][command] = dst; }
  int GetNext(int src, Command command) { return tr[src][command]; }

  void SetNodeMeaning(int node, int x, int y, int angle) {
    meaning[node].x = x;
    meaning[node].y = y;
    meaning[node].angle = angle;
  }

  int GetNodeMeaningX(int node) {
    return meaning[node].x;
  }
  int GetNodeMeaningY(int node) {
    return meaning[node].y;
  }
  int GetNodeMeaningAngle(int node) {
    return meaning[node].angle;
  }

 private:
  std::vector<std::array<int, 6> > tr;
  std::vector<Placement> meaning;
  int start_node;
};
