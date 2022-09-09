#include <cstdio>
#include <iostream>
int main(){
	double vel { }, tempo { }, consumo { };
	std::cin >> vel >> tempo >> consumo;

	double d = (vel * (tempo/60.0))/consumo;
	printf("%.2f\n", d);
	return 0;
}