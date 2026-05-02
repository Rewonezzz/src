#pragma once

#define PACKAGE "curl"
#define PACKAGE_BUGREPORT "a suitable curl mailing list: https://curl.se/mail/"
#define PACKAGE_NAME "curl"
#define PACKAGE_STRING "curl 7.79.0-DEV"
#define PACKAGE_TARNAME "curl"
#define PACKAGE_VERSION "7.79.0-DEV"
#define VERSION "7.79.0-DEV"

#define STDC_HEADERS 1
#define HAVE_STDLIB_H 1
#define HAVE_STDIO_H 1
#define HAVE_STRING_H 1
#define HAVE_STRINGS_H 1
#define HAVE_STDBOOL_H 1
#define HAVE_MEMORY_H 1
#define HAVE_SYS_TYPES_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_FCNTL_H 1
#define HAVE_TIME_H 1

#define HAVE_BOOL_T 1
#define HAVE_LONGLONG 1
#define SIZEOF_INT 4
#define SIZEOF_SHORT 2
#define SIZEOF_CURL_OFF_T 8
#define SIZEOF_TIME_T 8

#define ENABLE_IPV6 0
#define HAVE_GETADDRINFO 1
#define HAVE_FREEADDRINFO 1
#define HAVE_GETPEERNAME 1
#define HAVE_GETSOCKNAME 1
#define HAVE_STRUCT_TIMEVAL 1
#define HAVE_STRUCT_SOCKADDR_STORAGE 1

#define HAVE_ZLIB_H 1
#define HAVE_LIBZ 1

#if defined(_WIN64)
	#define OS "x86_64-pc-win32"
	#define SIZEOF_LONG 4
	#define SIZEOF_SIZE_T 8
#else
	#define OS "i386-pc-win32"
	#define SIZEOF_LONG 4
	#define SIZEOF_SIZE_T 4
#endif

#include <BaseTsd.h>
typedef SSIZE_T ssize_t;
#define HAVE_SSIZE_T 1
#if defined(_WIN64)
	#define SIZEOF_SSIZE_T 8
#else
	#define SIZEOF_SSIZE_T 4
#endif

#define HAVE_WINDOWS_H 1
#define HAVE_WINSOCK2_H 1
#define HAVE_WS2TCPIP_H 1
#define HAVE_IO_H 1
#define HAVE_PROCESS_H 1

#define HAVE_CLOSESOCKET 1
#define HAVE_IOCTLSOCKET 1
#define HAVE_IOCTLSOCKET_FIONBIO 1
#define HAVE_SELECT 1
#define HAVE_SOCKET 1
#define HAVE_RECV 1
#define HAVE_SEND 1

#define USE_WIN32_LARGE_FILES 1
#define USE_THREADS_WIN32 1
#define USE_WINDOWS_SSPI 1
#define USE_SCHANNEL 1
#define USE_WIN32_CRYPTO 1
#define USE_WIN32_IDN 1
#define WANT_IDN_PROTOTYPES 1

#define RECV_TYPE_RETV int
#define RECV_TYPE_ARG1 SOCKET
#define RECV_TYPE_ARG2 char *
#define RECV_TYPE_ARG3 int
#define RECV_TYPE_ARG4 int

#define SEND_TYPE_RETV int
#define SEND_QUAL_ARG2 const
#define SEND_TYPE_ARG1 SOCKET
#define SEND_TYPE_ARG2 char *
#define SEND_TYPE_ARG3 int
#define SEND_TYPE_ARG4 int

#define HAVE_STRICMP 1
#define HAVE_STRNICMP 1

#define HAVE_ERRNO_H 1

#define HAVE_FCNTL_H 1
