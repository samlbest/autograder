/************************************************************
** CS 419 Auto-grader project                              **
** Sam Best, Steve Dunbar, George Nix                      **
** Template for "student" programs to use as test samples  **
** for the autograder. Edit to change command-line options **
** accepted and to cause errors.                           **
*************************************************************/


#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <stdlib.h>

/************************************************************
** Uncomment appropriate line(s) to produce errors         **
*************************************************************/

//#define DELAY_TIME 3000   // delay time to cause grader to timeout
//#define COMPILE_FAIL      // compilation error
//#define SEGFAULT          // crashes
//#define EXECUTION_ERROR   // runs, then exits with an error code

int main(int argc, char** argv)
{

#ifdef DELAY_TIME
    sleep(DELAY_TIME);
#endif

#ifdef COMPILE_FAIL
    {
#endif

#ifdef SEGFAULT
    int* a;
    a = 0;
    int b = *a;
#endif

/************************************************************
** Change command-line options here                        **
** and in the string in the getoppt_long call              **
*************************************************************/

    static struct option long_options[] =
    {
        {"option_a", no_argument, NULL, 'a'},
        {"option_b", no_argument, NULL, 'b'},
        {"option_b", no_argument, NULL, 'c'},
        {"option_d", required_argument, NULL, 'd'},
        {"option_e", required_argument, NULL, 'e'},
        {"option_f", required_argument, NULL, 'f'},
    };

    int option_index = 0;
    int c;

    while ( (c = getopt_long(argc, argv, "abcd:e:f:", long_options, &option_index)) != -1) {
        if (c == 'a') {puts("Option a");}
        if (c == 'b') {puts("Option b");}
        if (c == 'c') {puts("Option c");}
        if (c == 'd') {puts("Option d"); puts(optarg);}
        if (c == 'e') {puts("Option e"); puts(optarg);}
        if (c == 'f') {puts("Option f"); puts(optarg);}

    }

#ifdef EXECUTION_ERROR
    exit(EXIT_FAILURE);
#endif

      exit(EXIT_SUCCESS);

}
