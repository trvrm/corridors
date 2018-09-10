#include "corridors_threaded_api.h"
#include <algorithm>

corridors_threaded_api::corridors_threaded_api(
    const double c,
    const Seed seed,
    const size_t min_simulations,
    const size_t max_simulations,
    const size_t sim_increment)
    : corridors_base(c,seed, min_simulations, max_simulations, sim_increment)
{
}

std::string corridors_threaded_api::display(const bool flip)
{
    return corridors_base::display(flip);
}

void corridors_threaded_api::make_move(const std::string & action_text, const bool flip)
{
    corridors_base::make_move(action_text, flip);
}

p::list corridors_threaded_api::get_sorted_actions(const bool flip)
{
    p::list ret;
    auto vect_list = corridors_base::get_sorted_actions(flip);
    std::for_each(vect_list.cbegin(), vect_list.cend(), [&](const auto & tuple)
    {
        ret.append(
            p::make_tuple(
                std::get<0>(tuple),
                std::get<1>(tuple),
                std::get<2>(tuple)
            )
        );
    });
    return ret;
}

void corridors_threaded_api::choose_best_action(const double epsilon)
{
    corridors_base::choose_best_action(epsilon);
}

void corridors_threaded_api::ensure_sims(const size_t sims)
{
    corridors_base::ensure_sims(sims);
}

double corridors_threaded_api::get_evaluation()
{
    return corridors_base::get_evaluation();
}
