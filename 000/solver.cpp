#include <iostream>
#include <vector>
#include <aux.hpp>  // https://raw.githubusercontent.com/senapk/cppaux/master/aux.hpp
using namespace aux;

//++0
bool in(std::vector<int> vet, int x) {
    for (auto elem : vet)
        if (elem == x) 
            return true;
    return false;
}

int index_of(std::vector<int> vet, int x) {
    for (int i = 0; i < (int) vet.size(); ++i)
        if (vet[i] == x) 
            return i;
    return -1;
}

int find_if(const std::vector<int>& vet) {
    for (int i = 0; i < (int) vet.size(); ++i)
        if (vet[i] > 0)
            return i;
    return -1;
}

int min_element(const std::vector<int>& vet) {
    int index = -1;
    for (int i = 0; i < (int) vet.size(); ++i)
        if (index == -1 || vet[i] < vet[index])
            index = i;
    return index;
}

int find_min_if(const std::vector<int>& vet) {
    int index = -1;
    for (int i = 0; i < (int) vet.size(); ++i)
        if (vet[i] > 0 && //homem
            (index == -1 || vet[i] < vet[index])) //primeiro ou melhor
            index = i;
    return index;
}

//==

//loop principal
int main(){
    Chain chain;
    Param ui;

    chain["in"]           = [&] { show <<          in(to_vet<int>(ui[1]), to<int>(ui[2])); };
    chain["index_of"]     = [&] { show <<    index_of(to_vet<int>(ui[1]), to<int>(ui[2])); };
    chain["find_if"]      = [&] { show <<     find_if(to_vet<int>(ui[1])                ); };
    chain["min_element"]  = [&] { show << min_element(to_vet<int>(ui[1])                ); };
    chain["find_min_if"]  = [&] { show << find_min_if(to_vet<int>(ui[1])                ); };

    execute(chain, ui);
}
