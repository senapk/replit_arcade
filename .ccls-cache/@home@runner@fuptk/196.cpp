#include <iostream>
#include <cstdio>
int main() {
	double total { };
	int parcelas { };
	std::cin >> total >> parcelas;

	double valor_final = total + total * ((parcelas - 1) * 5.0) / 100.0;
	double parcial = valor_final / parcelas;
	printf("%.2f\n%.1f\n", parcial, valor_final);
}