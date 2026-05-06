//===========================================================================//
// Lua net library — shared header.
//===========================================================================//
#ifndef LNET_SHARED_H
#define LNET_SHARED_H
#ifdef _WIN32
#pragma once
#endif

#include "bitbuf.h"

#define LUA_NET_MAX_PAYLOAD       (255 * 8)
#define LUA_NET_STRING_TABLE_BITS 12
#define LUA_NET_STRING_TABLE_MAX  (1 << LUA_NET_STRING_TABLE_BITS)

extern bf_write  *g_pLuaNetWriteBuf;
extern bf_read   *g_pLuaNetReadBuf;


int         LuaNet_GetStringID  ( const char *name );
const char *LuaNet_GetStringName( int id );
int         LuaNet_AddString    ( const char *name );

void LuaNet_DispatchReceive( lua_State *L, const char *name, int bits, CBasePlayer *pSender );

#endif // LNET_SHARED_H