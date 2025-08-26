#ifndef SWITCH_H_
#define SWITCH_H_

#include "vm.h"

#ifdef __GNUC__
# define SWITCH_WITH { void *__switch_labels__[] = {
# define BEGIN_SWITCH(x) }; goto *__switch_labels__[x];
# define CASE(x) __LABEL__ ## x
# define BREAK goto *__switch_labels__[uregs[PC]];
# define END_SWITCH };
#else
# define SWITCH_WITH
# define BEGIN_SWITCH(x) switch(x) {
# define CASE(x) x
# define BREAK break
# define END_SWITCH };
#endif

#endif /* SWITCH_H_ */
