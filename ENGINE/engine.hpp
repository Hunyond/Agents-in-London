
#pragma once

#include <tuple>
#include <vector>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <stdexcept>
#include <variant>
#include <pybind11/pybind11.h>

namespace py = pybind11;

// You likely already have this in C++.
// Placeholder example:
enum class TransportType : std::uint8_t {
    Taxi,
    Bus,
    Tube,
    Black,
    Double
};

class Move {
public:

    constexpr Move(int player,
                   int from_station,
                   int to_station,
                   TransportType type) noexcept
        : player_(player),
          from_station_(from_station),
          to_station_(to_station),
          type_(type) {}

    // Getters
    constexpr int player() const noexcept { return player_; }
    constexpr int from_station() const noexcept { return from_station_; }
    constexpr int to_station() const noexcept { return to_station_; }
    constexpr TransportType type() const noexcept { return type_; }


private:
    int player_;
    int from_station_;
    int to_station_;
    TransportType type_;
};

struct PlayerCards {
    int taxi  = 0;
    int bus   = 0;
    int tube  = 0;
    int black = 0;
    int x2    = 0;
};

class GameState {
private:
    int turn_;
    std::vector<int> player_locs_;
    std::vector<PlayerCards> player_cards_;
    int current_player_;
    bool victory_flag_;
public:

    // Immutable (frozen=True equivalent): no setters provided.
    GameState(int turn,
              std::vector<int> player_locs,
              std::vector<PlayerCards> player_cards,
              int current_player,
              bool victory_flag)
        : turn_(turn),
          player_locs_(std::move(player_locs)),
          player_cards_(std::move(player_cards)),
          current_player_(current_player),
          victory_flag_(victory_flag) {}

    // Getters
    int turn() const noexcept { return turn_; }

    // Locations: player_locs_[i] = station id of player i
    const std::vector<int>& player_locs() const noexcept { return player_locs_; }

    // Cards: player_cards_[i] = tickets of player i
    const std::vector<PlayerCards>& player_cards() const noexcept { return player_cards_; }

    int current_player() const noexcept { return current_player_; }

    bool victory_flag() const noexcept { return victory_flag_; }

    std::size_t player_count() const noexcept { return player_locs_.size(); }


};

class Agent {
public:
    using CppCb = std::function<Move(const GameState&)>;
    using PyCb  = py::function;
    using Callback = std::variant<std::monostate, CppCb, PyCb>;
    std::variant<std::function<Move(const GameState&)>,  callback;

    Move operator()(const GameState& state) const {
    return std::visit([&](auto const& f) -> Move {
        using T = std::decay_t<decltype(f)>;

        if constexpr (std::is_same_v<T, std::monostate>) {
            throw std::runtime_error("Callback not set");
        } else if constexpr (std::is_same_v<T, CppCb>) {
            return f(state); // no GIL
        } else { // PyCb
            py::gil_scoped_acquire gil;
            return f(state).cast<Move>();
        }
    }, cb);
}

private:
    Callback cb{std::monostate{}};
};




class Engine {
    private:
        std::vector<Agent> agnets;
        GameState currentState;
    public:
};