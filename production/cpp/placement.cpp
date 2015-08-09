#include "placement.h"

#include <map>
#include <iostream>
#include <algorithm>

using namespace std;


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
