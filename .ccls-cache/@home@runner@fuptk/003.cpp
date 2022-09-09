#include <stdio.h>

int main(){
	double vel = 0.0, tempo = 0.0, consumo = 0.0;
	scanf("%f %f %f", &vel, &tempo, &consumo);

	double d = (vel * (tempo/60.0))/consumo + 1;
	printf("%.2f\n", d);
	return 0;
}