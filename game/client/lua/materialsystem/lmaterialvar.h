//========== Copyright (C) 2026, Team HL2SB++, All rights reserved. ===========//
//
// Purpose:
//
//===========================================================================//
#ifndef LMATERIALVAR_H
#define LMATERIALVAR_H
#ifdef _WIN32
#pragma once
#endif


/*
** access functions (stack -> C)
*/

LUALIB_API IMaterialVar *luaL_checkmaterialvar( lua_State *L, int idx );



/*
** push functions (C -> stack)
*/

LUA_API void          lua_pushmaterialvar  ( lua_State *L, IMaterialVar *pVar );

#endif // LMATERIALVAR_H