//========== Copyright (C) 2026, Team HL2SB++, All rights reserved. ===========//
//
// Purpose:
//
//=============================================================================//
#include "cbase.h"
#include "bugreporter_ui.h"
#include "webmanager.h"
#include "sbpp_globaldef.h"

#include <vgui/IScheme.h>
#include <vgui/ISurface.h>
#include <vgui/IInput.h>
#include <vgui/IVGui.h>
#include <vgui/ILocalize.h>
#include <vgui_controls/Label.h>
#include <vgui_controls/TextEntry.h>
#include <vgui_controls/Button.h>
#include <vgui_controls/MessageBox.h>
#include "ienginevgui.h"
#include <vgui/IVGui.h>

#include "tier0/memdbgon.h"

using namespace vgui;

const char *CBugReportPanel::kBugReportUrl = "https://workshop-bot.sbpp-workshop.workers.dev/bug-report";

static const int kTitleMin = 3;
static const int kTitleMax = 120;
static const int kDescMin = 10;
static const int kDescMax = 4000;
static const int kReporterMax = 64;
static const int kAddonIdMax = 32;
static const int kVersionMax = 32;

static void GetEntryText( TextEntry *pEntry, char *out, int outSize )
{
	if ( !pEntry )
	{
		out[0] = 0;
		return;
	}
	pEntry->GetText( out, outSize );
}

static void JsonEscape( const char *src, char *dst, int dstSize )
{
	int j = 0;
	for ( int i = 0; src[i] && j < dstSize - 7; i++ )
	{
		unsigned char c = (unsigned char)src[i];
		switch ( c )
		{
		case '\"':
			dst[j++] = '\\';
			dst[j++] = '\"';
			break;
		case '\\':
			dst[j++] = '\\';
			dst[j++] = '\\';
			break;
		case '\n':
			dst[j++] = '\\';
			dst[j++] = 'n';
			break;
		case '\r':
			dst[j++] = '\\';
			dst[j++] = 'r';
			break;
		case '\t':
			dst[j++] = '\\';
			dst[j++] = 't';
			break;
		case '\b':
			dst[j++] = '\\';
			dst[j++] = 'b';
			break;
		case '\f':
			dst[j++] = '\\';
			dst[j++] = 'f';
			break;
		default:
			if ( c < 0x20 )
				j += Q_snprintf( dst + j, dstSize - j, "\\u%04x", c );
			else
				dst[j++] = c;
		}
	}
	dst[j] = 0;
}

CBugReportPanel::CBugReportPanel( Panel *parent ) : BaseClass( parent, "BugReportPanel" )
{
	SetProportional( true );

	SetTitle( "#SBPP_BugReport_Title", true );
	SetSizeable( false );
	SetMoveable( true );
	SetDeleteSelfOnClose( false );
	SetVisible( false );

	m_bSubmitting = false;

	m_pLblName = new Label( this, "LblName", "#SBPP_BugReport_Name" );
	m_pName = new TextEntry( this, "Name" );
	m_pName->SetMaximumCharCount( kReporterMax );

	m_pLblTitle = new Label( this, "LblTitle", "#SBPP_BugReport_BugTitle" );
	m_pTitle = new TextEntry( this, "Title" );
	m_pTitle->SetMaximumCharCount( kTitleMax );

	m_pLblAddonId = new Label( this, "LblAddonId", "#SBPP_BugReport_AddonId" );
	m_pAddonId = new TextEntry( this, "AddonId" );
	m_pAddonId->SetMaximumCharCount( kAddonIdMax );

	m_pLblVersion = new Label( this, "LblVersion", "#SBPP_BugReport_Version" );
	m_pVersion = new TextEntry( this, "Version" );
	m_pVersion->SetMaximumCharCount( kVersionMax );

	m_pLblDescription = new Label( this, "LblDescription", "#SBPP_BugReport_Description" );
	m_pDescription = new TextEntry( this, "Description" );
	m_pDescription->SetMultiline( true );
	m_pDescription->SetCatchEnterKey( true );
	m_pDescription->SetVerticalScrollbar( true );
	m_pDescription->SetMaximumCharCount( kDescMax );

	m_pSubmit = new Button( this, "Submit", "#SBPP_BugReport_Submit", this, "submit" );
	m_pCancel = new Button( this, "Cancel", "#SBPP_BugReport_Cancel", this, "cancel" );

	LoadControlSettings( "resource/ui/BugReportPanel.res" );
	SetVisible( false );
}

CBugReportPanel::~CBugReportPanel()
{
}

void CBugReportPanel::Activate()
{
	BaseClass::Activate();
	MoveToCenterOfScreen();
	RequestFocus();
	if ( m_pName )
		m_pName->RequestFocus();
}

void CBugReportPanel::ApplySchemeSettings( IScheme *pScheme )
{
	BaseClass::ApplySchemeSettings( pScheme );
}

void CBugReportPanel::PerformLayout()
{
	BaseClass::PerformLayout();
}

void CBugReportPanel::OnCommand( const char *command )
{
	if ( !Q_stricmp( command, "cancel" ) )
	{
		ClearForm();
		SetVisible( false );
		return;
	}
	if ( !Q_stricmp( command, "submit" ) )
	{
		SubmitReport();
		return;
	}
	BaseClass::OnCommand( command );
}

void CBugReportPanel::ClearForm()
{
	m_pName->SetText( "" );
	m_pTitle->SetText( "" );
	m_pAddonId->SetText( "" );
	m_pVersion->SetText( "" );
	m_pDescription->SetText( "" );
}

void CBugReportPanel::ShowInfo( const char *title, const char *text )
{
    MessageBox *pBox = new MessageBox( title, text, NULL );
    pBox->SetParent( enginevgui->GetPanel( PANEL_GAMEUIDLL ) );
    pBox->MakePopup( false, true );
    pBox->MoveToFront();
    pBox->SetOKButtonVisible( true );
    pBox->SetCloseButtonVisible( false );
    pBox->DoModal();
}

void CBugReportPanel::ShowError( const char *title, const char *text )
{
    MessageBox *pBox = new MessageBox( title, text, NULL );
    pBox->SetParent( enginevgui->GetPanel( PANEL_GAMEUIDLL ) );
    pBox->MakePopup( false, true );
    pBox->MoveToFront();
    pBox->SetOKButtonVisible( true );
    pBox->SetCloseButtonVisible( false );
    pBox->DoModal();
}

void CBugReportPanel::SubmitReport()
{
	if ( m_bSubmitting )
		return;

	char name[128], title[256], addon[64], version[64];
	char description[kDescMax + 16];

	GetEntryText( m_pName, name, sizeof( name ) );
	GetEntryText( m_pTitle, title, sizeof( title ) );
	GetEntryText( m_pAddonId, addon, sizeof( addon ) );
	GetEntryText( m_pVersion, version, sizeof( version ) );
	GetEntryText( m_pDescription, description, sizeof( description ) );

	int nameLen = Q_strlen( name );
	int titleLen = Q_strlen( title );
	int descLen = Q_strlen( description );

	if ( nameLen < 1 )
	{
		ShowError( "#SBPP_BugReport_ErrTitle", "Please enter your name." );
		return;
	}
	if ( titleLen < kTitleMin || titleLen > kTitleMax )
	{
		char buf[128];
		Q_snprintf( buf, sizeof( buf ), "Title must be %d-%d characters.", kTitleMin, kTitleMax );
		ShowError( "#SBPP_BugReport_ErrTitle", buf );
		return;
	}
	if ( descLen < kDescMin || descLen > kDescMax )
	{
		char buf[128];
		Q_snprintf( buf, sizeof( buf ), "Description must be %d-%d characters.", kDescMin, kDescMax );
		ShowError( "#SBPP_BugReport_ErrTitle", buf );
		return;
	}

	if ( !g_pWebManager )
		return;

	char eName[256], eTitle[512], eAddon[128], eVersion[128];
	char eDesc[kDescMax * 2 + 16];

	JsonEscape( name, eName, sizeof( eName ) );
	JsonEscape( title, eTitle, sizeof( eTitle ) );
	JsonEscape( addon, eAddon, sizeof( eAddon ) );
	JsonEscape( version, eVersion, sizeof( eVersion ) );
	JsonEscape( description, eDesc, sizeof( eDesc ) );

	char body[kDescMax * 2 + 1024];
	Q_snprintf( body, sizeof( body ),
		"{"
		"\"reporter\":\"%s\","
		"\"title\":\"%s\","
		"\"description\":\"%s\","
		"\"addon_id\":\"%s\","
		"\"version\":\"%s\""
		"}",
		eName, eTitle, eDesc, eAddon, eVersion );

	m_bSubmitting = true;
	m_pSubmit->SetEnabled( false );
	m_pCancel->SetEnabled( false );

	bool ok = g_pWebManager->Post( kBugReportUrl, body,
		[]( bool success, const std::string &response )
		{
			(void)success;
			(void)response;
		} );

	m_bSubmitting = false;
	m_pSubmit->SetEnabled( true );
	m_pCancel->SetEnabled( true );

	if ( ok )
	{
		ShowInfo( "#SBPP_BugReport_OkTitle", "Bug report sent! Thank you." );
		ClearForm();
		SetVisible( false );
	}
	else
	{
		ShowError( "#SBPP_BugReport_ErrTitle", "Failed to send. Check your internet connection and try again." );
	}
}

//---

static CBugReportPanel *g_pBugReportPanel = NULL;

CON_COMMAND( sbpp_bugreport, "Open the bug report panel" )
{
	if ( !g_pBugReportPanel )
	{
		VPANEL gameUiRoot = enginevgui->GetPanel( PANEL_GAMEUIDLL );
		g_pBugReportPanel = new CBugReportPanel( NULL );
		g_pBugReportPanel->SetParent( gameUiRoot );
	}

	g_pBugReportPanel->Activate();
	g_pBugReportPanel->SetVisible( true );
	g_pBugReportPanel->MoveToFront();
	g_pBugReportPanel->MakePopup( false, true );
}
