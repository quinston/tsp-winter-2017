#include<stdio.h>
#include<stdlib.h>
extern int DPseparator (int nnodes, int nedges, int* edges, double* weigh, int* nIneq,
    int** nDominoes, int*** nAset, int*** nBset, int** nHandle, int**** Aset,
    int **** Bset, int*** Handle, const char *boss_name, double percentage,    
    double ddp_heuristic_maxtime);

/*
int nnodes = 6;
int nedges = 9;
int edges[] = { 0, 1, 0, 2, 1, 2, 0,4, 2,3,1,5,3,4,3,5,4,5 };
double weigh[] = { .5, .5, .5, 1, 1, 1, .5, .5, .5 };
*/

int less(const void* a, const void* b) {
	int c = *((const int*) a);
	int d = *((const int*) b);
	if (c > d) return 1;
	if (c==d) return 0;
	return -1;
}

int main() {
	int nnodes;
	int nedges;
	int* edges;
	double* weigh;

	scanf("%d", &nnodes);
	scanf("%d", &nedges);
	edges = malloc(sizeof(int) * nedges * 2);
	weigh = malloc(sizeof(double) * nedges);
	for (int i = 0; i < nedges; ++i) {
		scanf("%d", &(edges[2*i]));
		scanf("%d", &(edges[2*i + 1]));
		scanf("%lf", &(weigh[i]));
	}

	int nIneq;
	int*  nDominoes;
	int** nAset, **nBset, *nHandle, ***Aset, ***Bset, **Handle;

	DPseparator(nnodes, nedges, edges, weigh,
&nIneq, &nDominoes, &nAset, &nBset, &nHandle,
&Aset, &Bset, &Handle, 
NULL, 0.96, 10);
	printf("Number of inequalti %d\n", nIneq);
	for (int numIneq = 0; numIneq < nIneq; ++numIneq) {
		printf("Handle size %d\n ", nHandle[numIneq]);
		/* SOrt the vertices */
		qsort(Handle[numIneq], nHandle[numIneq], sizeof(int), &less);
		for (int numVertexInHandle = 0; numVertexInHandle < nHandle[numIneq]; ++numVertexInHandle) {
			/* I one-index my vertices */
			printf("%d ", Handle[numIneq][numVertexInHandle] + 1);
		}
		putchar('\n');
		for (int numDomino = 0; numDomino < nDominoes[numIneq]; ++numDomino) {
			printf("A size %d\n ", nAset[numIneq][numDomino]);
			qsort(Aset[numIneq][numDomino], nAset[numIneq][numDomino], sizeof(int), &less);

			for (int numVertex = 0; numVertex < nAset[numIneq][numDomino]; ++numVertex) {
				printf("%d ", Aset[numIneq][numDomino][numVertex] + 1);
			}
			putchar('\n');
			printf("B size %d\n ", nBset[numIneq][numDomino]);
			qsort(Bset[numIneq][numDomino], nBset[numIneq][numDomino], sizeof(int), &less);

			for (int numVertex = 0; numVertex < nBset[numIneq][numDomino]; ++numVertex) {
				printf("%d ", Bset[numIneq][numDomino][numVertex] + 1);
			}
			putchar('\n');
		}
	}
	return 0;
}
