python3 -m production.ui --problem qualifier/problem_${1}.json \
                         --prompt_for_submit                   \
                         --seed "${2}"                         \
                         --moves "${3}"                        \
                         --delay=0.001
