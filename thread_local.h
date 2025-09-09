#ifndef THREAD_LOCAL_H__
#define THREAD_LOCAL_H__

#if defined(__GNUC__)
# define thread_local __thread
#elif defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
# define thread_local thread_local
#else
# warning "No thread local support"
# define thread_local
#endif

#endif
