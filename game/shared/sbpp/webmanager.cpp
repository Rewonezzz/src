//========== Copyright (C) 2026, Team HL2SB++, All rights reserved. ===========//
//
// Purpose:
//
//===========================================================================//

#include "cbase.h"
#include "webmanager.h"
#include "filesystem.h"
#include "sbpp_globaldef.h"

CWebManager::CWebManager()
{
}

CWebManager::~CWebManager()
{
	Shutdown();
}

bool CWebManager::Init()
{
	return curl_global_init( CURL_GLOBAL_DEFAULT ) == 0;
}

void CWebManager::Shutdown()
{
	curl_global_cleanup();
}

size_t CWebManager::WriteMemoryCallback( void *contents, size_t size, size_t nmemb, void *userp )
{
	size_t		 totalSize = size * nmemb;
	std::string *mem = (std::string *)userp;

	mem->append( (char *)contents, totalSize );

	return totalSize;
}

size_t CWebManager::WriteFileCallback( void *contents, size_t size, size_t nmemb, void *userp )
{
	size_t totalSize = size * nmemb;

	FileHandle_t file = (FileHandle_t)userp;

	g_pFullFileSystem->Write( contents, totalSize, file );

	return totalSize;
}

bool CWebManager::PerformRequest( CURL *curl )
{
	CURLcode res = curl_easy_perform( curl );

	if ( res != CURLE_OK )
		return false;

	long response_code = 0;
	curl_easy_getinfo( curl, CURLINFO_RESPONSE_CODE, &response_code );

	return response_code == 200;
}

bool CWebManager::Get( const std::string &url, RequestCallback callback )
{
	CURL *curl = curl_easy_init();

	if ( !curl )
		return false;

	FileHandle_t hFile = g_pFullFileSystem->Open( "settings/cacert.pem", "rb", "GAME" );
	if ( hFile )
	{
		int	  nSize = g_pFullFileSystem->Size( hFile );
		char *pBuf = new char[nSize];
		g_pFullFileSystem->Read( pBuf, nSize, hFile );
		g_pFullFileSystem->Close( hFile );

		struct curl_blob blob;
		blob.data = pBuf;
		blob.len = nSize;
		blob.flags = CURL_BLOB_COPY;

		curl_easy_setopt( curl, CURLOPT_CAINFO_BLOB, &blob );

		delete[] pBuf;
	}

	std::string response;

	curl_easy_setopt( curl, CURLOPT_URL, url.c_str() );
	curl_easy_setopt( curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback );
	curl_easy_setopt( curl, CURLOPT_WRITEDATA, &response );

	// TODO: maybe change it once every version comes out...?
	curl_easy_setopt( curl, CURLOPT_USERAGENT, "HL2SBPP/1.1" );

	curl_easy_setopt( curl, CURLOPT_FOLLOWLOCATION, 1L );

	curl_easy_setopt( curl, CURLOPT_SSL_VERIFYPEER, 1L );
	curl_easy_setopt( curl, CURLOPT_SSL_VERIFYHOST, 2L );

	curl_easy_setopt( curl, CURLOPT_CONNECTTIMEOUT, 10L );
	curl_easy_setopt( curl, CURLOPT_TIMEOUT, 30L );

	bool success = PerformRequest( curl );

	curl_easy_cleanup( curl );

	callback( success, response );

	return success;
}

bool CWebManager::DownloadToFile( const std::string &url, const std::string &filePath )
{
	CURL *curl = curl_easy_init();

	if ( !curl )
		return false;

	FileHandle_t file = g_pFullFileSystem->Open( filePath.c_str(), "wb" );

	if ( !file )
	{
		curl_easy_cleanup( curl );
		return false;
	}

	curl_easy_setopt( curl, CURLOPT_URL, url.c_str() );
	curl_easy_setopt( curl, CURLOPT_WRITEFUNCTION, WriteFileCallback );
	curl_easy_setopt( curl, CURLOPT_WRITEDATA, file );

	curl_easy_setopt( curl, CURLOPT_FOLLOWLOCATION, 1L );

	bool success = PerformRequest( curl );

	g_pFullFileSystem->Close( file );

	curl_easy_cleanup( curl );

	return success;
}
