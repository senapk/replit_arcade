#include <iostream>
int main() {
	int posicoes { }, disco { }, aviao { };
	std::cin >> posicoes >> disco >> aviao;
	if (aviao > disco)
		aviao -= posicoes;
	std::cout << (disco - aviao) << '\n';
}