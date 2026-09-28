BANKS = [
    # Working URLs with improved structure
    {"name": "Société Tunisienne de Banque (STB)", "url": "https://www.stb.com.tn/fr/", "language": "fr", "news_selector": "//*[contains(@class, 'actualite') or contains(@class, 'news')]"},
    {"name": "Banque Nationale Agricole (BNA)", "url": "http://www.bna.tn/site/fr/news.php", "language": "fr", "specific_page": True},
    {"name": "Banque de l'Habitat (BH)", "url": "https://www.bhbank.tn/", "language": "fr/ar"},
    {"name": "Banque de Financement des PMEs (BFPME)", "url": "https://bfpme.com.tn/", "language": "fr"},
    {"name": "Banque Tunisienne de Solidarité (BTS)", "url": "https://www.bts.com.tn/", "language": "fr/ar"},
    {"name": "Banque de Tunisie et des Émirats (BTE)", "url": "https://www.bte.com.tn/", "language": "fr"},
    {"name": "Banque Tuniso-Libyenne (BTL)", "url": "https://btl.tn/", "language": "fr/ar"},
    {"name": "Tunisian Saudi Bank (TSB)", "url": "https://www.tsb.com.tn/fr/actualites", "language": "fr", "specific_page": True},
    {"name": "Banque Zitouna", "url": "https://www.zitounabank.com.tn/fr/actualites", "language": "fr", "skip_ssl": True, "specific_page": True},
    {"name": "Al Baraka Bank", "url": "https://www.albaraka.com.tn/", "language": "fr/ar"},
    {"name": "Al Wifak International Bank", "url": "https://www.wifakbank.com/", "language": "fr/ar"},
    {"name": "Amen Bank", "url": "https://www.amenbank.com.tn/fr/actualites", "language": "fr", "skip_ssl": True, "specific_page": True},
    {"name": "Attijari Bank", "url": "https://www.attijaribank.com.tn/fr/actualites", "language": "fr", "specific_page": True},
    {"name": "Arab Tunisian Bank (ATB)", "url": "https://www.atb.tn/fr/actualites", "language": "fr", "timeout_extended": True, "specific_page": True},
    {"name": "Banque Internationale Arabe de Tunisie (BIAT)", "url": "https://www.biat.com.tn/fr/actualites", "language": "fr", "specific_page": True},
    {"name": "Banque de Tunisie (BT)", "url": "https://www.bt.com.tn/fr/actualites", "language": "fr", "specific_page": True},
    {"name": "Banque Tuniso-Koweïtienne (BTK)", "url": "https://www.btkbank.com/", "language": "fr/ar"},
    {"name": "Qatar National Bank – Tunis (QNB-Tunis)", "url": "https://www.qnb.com.tn/sites/qnb/qnbtunisia/page/fr/fr-home.html", "language": "fr/ar", "timeout_extended": True},
    {"name": "Union Bancaire de Commerce et d'Industrie (UBCI)", "url": "https://www.ubci.com/", "language": "fr"},
    {"name": "Union Internationale de Banque (UIB)", "url": "https://www.uib.com.tn/fr/actualites", "language": "fr", "specific_page": True}
]

# Additional campaign-specific URLs
CAMPAIGN_URLS = {
    "Attijari Bank": "https://www.attijaribank.com.tn/fr/particulier/offre-packagee",
    "Banque Zitouna": "https://www.zitounabank.com.tn/fr/promotions",
    "Amen Bank": "https://www.amenbank.com.tn/fr/promotions",
    "BIAT": "https://www.biat.com.tn/fr/promotions",
    "ATB": "https://www.atb.tn/fr/promotions"
}

def verify_urls():
    """Check all URLs are accessible with improved verification"""
    import requests
    from urllib.parse import urlparse
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print("Verifying bank URLs with enhanced checks...")
    print("-" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,ar;q=0.8,en;q=0.5,en-US;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for bank in BANKS:
        try:
            # Handle SSL skipping for problematic banks
            verify_ssl = not bank.get('skip_ssl', False)
            
            # Try HEAD first, then GET if needed
            try:
                response = requests.head(bank["url"], headers=headers, timeout=15, 
                                      allow_redirects=True, verify=verify_ssl)
                
                if response.status_code == 405:  # HEAD not allowed
                    response = requests.get(bank["url"], headers=headers, timeout=15, 
                                         allow_redirects=True, verify=verify_ssl)
            except requests.exceptions.SSLError:
                if bank.get('skip_ssl', False):
                    response = requests.get(bank["url"], headers=headers, timeout=15, 
                                         allow_redirects=True, verify=False)
                else:
                    raise
            
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            final_url = response.url
            ssl_status = " (no SSL)" if not verify_ssl else ""
            print(f"{bank['name'][:35]:<35} {status}{ssl_status} -> {final_url}")
            
        except requests.exceptions.SSLError:
            print(f"{bank['name'][:35]:<35} ⚠️  SSL ERROR - marked for skip_ssl")
            
        except requests.exceptions.ConnectionError:
            print(f"{bank['name'][:35]:<35} ❌ CONNECTION FAILED")
            
        except requests.exceptions.Timeout:
            print(f"{bank['name'][:35]:<35} ⏰ TIMEOUT")
            
        except Exception as e:
            print(f"{bank['name'][:35]:<35} ❌ ERROR: {str(e)[:30]}...")

if __name__ == "__main__":
    verify_urls()