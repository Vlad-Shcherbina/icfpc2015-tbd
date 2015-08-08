#pragma once

#include <array>
#include <vector>

struct Graph {
  Graph(int size) : tr(size) {}

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

  void SetNext(int src, Command command, int dst) { tr[src][command] = dst; }
  int GetNext(int src, Command command) { return tr[src][command]; }

 private:
  std::vector<std::array<int, 6> > tr;
  int start_node;
};
