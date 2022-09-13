#pragma once

#include <iostream>
#include <sstream>
#include <map>
#include <vector>
#include <functional>

namespace aux {
    using Chain = std::map<std::string, std::function<void()>>;
    using Param = std::vector<std::string>;

    std::vector<std::string> __split(const std::string& line, char delimiter) {
        std::istringstream is(line);
        std::vector<std::string> output;
        std::string token;
        while(std::getline(is, token, delimiter))
            output.push_back(token);
        return output;
    };

    void __action(Chain& chain, Param& ui, bool on_moodle) {
        while(true) {
            std::string line{}, cmd{};
            if (!on_moodle)
                std::cout << "$";
            std::getline(std::cin, line);
            std::stringstream ss(line);
            ss >> cmd;
            ui = __split(line, ' ');
            if (on_moodle)
                std::cout << "$" << line << '\n';
            if (cmd == "end") {
                break;
            } else if (chain.count(cmd) != 0) {
                try {
                    chain[cmd]();
                } catch (std::string& e) {
                    std::cout << e << '\n';
                }
            } else {
                std::cout << "fail: command not found\n";
            }
        }
    }

    void shell(Chain& chain, Param& ui) {
        __action(chain, ui, false);
    }

    void execute(Chain& chain, Param& ui) {
        __action(chain, ui, true);
    }
}

#pragma once

#include <iostream> //string
#include <sstream>  //stringstream
#include <vector>   //vector
#include <iomanip>  //setprecision
#include <functional>

namespace aux {

    template<typename T>
    std::string fmt(T value) {
        std::stringstream ss;
        ss << value;
        return ss.str();
    }

    template <>
    std::string fmt(bool value) {
        return value ? "true" : "false";
    }

    template <>
    std::string fmt(double value) {
        std::stringstream ss;
        ss << std::fixed << std::setprecision(2) << value;
        return ss.str();
    }

    template <>
    std::string fmt(float value) {
        return fmt((double) value);
    }

    template <typename K, typename T>
    std::string fmt(std::pair<K,T> value) {
        return fmt(value.first) + ":" + fmt(value.second);
    }

    template <class T>
    std::string fmt(std::vector<T> vet, std::string sep = ", ") {
        std::string prefix = "[";
        std::string suffix = "]";
        if(vet.size() == 0)
            return prefix + suffix;
        std::stringstream ss;
        for (const auto& item : vet)
            ss << sep << fmt(item);
        return prefix + ss.str().substr(sep.size()) + suffix;
    }

    struct Show {
    };

    Show show;

    template <class T>
    Show& operator<<(Show& show, T&& data) {
        std::cout << fmt(data) << '\n';
        return show;
    }

}

#pragma once

#include <iostream>
#include <sstream>
#include <vector>

namespace aux {
    template <class T>
    T to(std::string data) {
        T value;
        std::stringstream(data) >> value;
        return value;
    }

    template <>
    bool to(std::string data) {
        return data == "true";
    }

    template <class T>
    std::vector<T> to_vet(std::string data, char delimiter = ',') {
        std::istringstream is(data.substr(1, data.size() - 2));
        std::vector<T> output;
        std::string token;
        while(std::getline(is, token, delimiter))
            output.push_back(aux::to<T>(token));
        return output;
    }
}

#pragma once

#include <iostream>
#include <sstream>
#include <vector>
#include <algorithm>

namespace aux {

    template<typename CONTAINER, typename LAMBDA>
    auto map(CONTAINER&& container, LAMBDA&& fn){
        std::vector<decltype(fn(*container.begin()))> aux;
        std::transform(container.begin(), container.end(), std::back_inserter(aux), fn);
        return aux;
    };

    template<typename CONTAINER, typename LAMBDA>
    auto filter(CONTAINER&& container, LAMBDA&& pred){
        auto fn = [](auto x) {return x;}; 
        std::vector<decltype(fn(*container.begin()))> aux;
        std::copy_if(container.begin(), container.end(), std::back_inserter(aux), pred);
        return aux;
    };

    template<typename LAMBDA1, typename CONTAINER, typename LAMBDA2>
    auto clist(LAMBDA1&& fn, CONTAINER&& container, LAMBDA2&& pred){ 
        std::vector<decltype(fn(*container.begin()))> aux;
        for (auto&& elem : container)
            if (pred(elem))
                aux.push_back(fn(elem));
        return aux;
    };

    template<typename CONTAINER, typename LAMBDA, typename ELEM>
    auto foldl(CONTAINER&& container, LAMBDA&& fn, ELEM&& init){
        auto aux = init;
        for (auto&& elem : container)
            aux = fn(aux, elem);
        return aux;
    };

    template<typename CONTAINER, typename LAMBDA>
    auto foreach(CONTAINER&& container, LAMBDA&& fn){
        for (auto&& elem : container)
            fn(elem);
    };

    template<typename CONTAINER1, typename CONTAINER2>
    auto zip(CONTAINER1&& container1, CONTAINER2&& container2){
        std::vector<std::pair<decltype(*container1.begin()), decltype(*container2.begin())>> aux;
        auto it1 = container1.begin();
        auto it2 = container2.begin();
        while (it1 != container1.end() && it2 != container2.end())
            aux.push_back(std::make_pair(*it1++, *it2++));
        return aux;
    };

    // extrai um subvetor
    // extrai de início a fim, sem incluir o final
    // se não for passado o final, extrai até o final
    // se não for passado o início, extrai do início ao final
    // se o índice for negativo, conta a partir do final como no python e no js
    template <typename T>
    std::vector<T> slice(const std::vector<T>& container, int start = 0, int end = 0) {
        std::vector<T> result;
        if (end == 0)
            end = container.size();
        if (start < 0)
            start = container.size() + start;
        if (end < 0)
            end = container.size() + end;
        if (start >= end)
            return result;
        auto it_start = container.begin();
        auto it_end = container.begin();
        std::advance(it_start, start);
        std::advance(it_end, end);
        std::copy(it_start, it_end, std::back_inserter(result));
        return result;
    }

    std::vector<std::string> split(const std::string& line, char delimiter) {
        std::istringstream is(line);
        std::vector<std::string> output;
        std::string token;
        while(std::getline(is, token, delimiter))
            output.push_back(token);
        return output;
    }
}

