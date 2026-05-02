//========== Copyright (C) 2026, Team HL2SB++, All rights reserved. ===========//
//
// Purpose:
//
//===========================================================================//

#ifndef WEBMANAGER_H
#define WEBMANAGER_H
#ifdef _WIN32
#pragma once
#endif // _WIN32

#include <string>
#include <functional>
#include <curl/curl.h>

class IFileSystem;

class CWebManager
{
public:
	using RequestCallback = std::function< void( bool success, const std::string &response ) >;

	CWebManager();
	~CWebManager();

	bool Init();
	void Shutdown();

	bool Get( const std::string &url, RequestCallback callback );
	bool Post( const std::string &url, const std::string &jsonBody, RequestCallback callback );

	bool DownloadToFile( const std::string &url, const std::string &filePath );

private:
	static size_t WriteMemoryCallback( void *contents, size_t size, size_t nmemb, void *userp );
	static size_t WriteFileCallback( void *contents, size_t size, size_t nmemb, void *userp );

	bool PerformRequest( CURL *curl );
};

#endif // WEBMANAGER_H