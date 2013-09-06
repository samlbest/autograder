#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>


int main(int argc, char *argv[]) {
  //data
  const char* name[4];
  name[0] = "Sabin";
  name[1] = "Edgar";
  name[2] = "Terra";
  name[3] = "Celes";
  
  int age[4];
  age[0]= 24;
  age[1]= 29;
  age[2]= 19;
  age[3]= 23;

  int weight[4];
  weight[0]= 235;
  weight[1]= 175;
  weight[2]= 105;
  weight[3]= 110;

  int height[4];
  height[0] = 73;
  height[1] = 70;
  height[2] = 62;
  height[3] = 64;


  //parse args
  int aflag = 0;
  int wflag = 0;
  int hflag = 0;
  int c;
  int i;

  while ((c = getopt(argc,argv,"awh")) != -1)
    switch (c) {
    case 'a':
      aflag=1;
      break;
    case 'w':
      wflag=1;
      break;
    case 'h':
      hflag=1;
      break;
    default:
      abort();
    }
  
  for (i=0;i<4;i++) {
    printf("name:%s ",name[i]);
    if (aflag==1) {
      printf("age:%d years ",age[i]);
    }
    if (wflag==1) {
      printf("weight:%d pounds ",weight[i]);
    }
    if (hflag==1) {
      printf("height:%d inches ",height[i]);
    }
    printf("\n");
  }

  return 0;
}
