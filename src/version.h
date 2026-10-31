#ifndef VERSION_H
#define VERSION_H

#define		VERSION_MAJOR		3
#define		VERSION_MINOR		0
#define		VERSION_PATCH		2
// #define		VERSION_CANDIDATE	1			// Optional
// #define		VERSION_TYPE		"Beta "     // RC, Alpha, Beta, etc.

#define		VERSION_VARIANT		"Platform"
#if defined(UART0_EXPERIMENTAL_BRANDING)
#define     VERSION_SUBTITLE    "Arthur - UART0 OTIRX EXPERIMENTAL ABI1.2"
#else
#define     VERSION_SUBTITLE    "Arthur"
#endif

#endif // VERSION_H
