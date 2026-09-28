import os
import json
import csv
from datetime import datetime
from scraper import BankScraper
from banks import BANKS
from cosmos_client import CosmosDBClient  # Add this import

OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_results(results, format='both'):
    """Save results in JSON and CSV formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON output
    json_path = os.path.join(OUTPUT_DIR, f"bank_results_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # CSV output
    if format in ['both', 'csv']:
        csv_path = os.path.join(OUTPUT_DIR, f"bank_results_{timestamp}.csv")
        with open(csv_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Bank', 'URL', 'Status', 'News Count', 'Campaigns Count', 'Updates Count', 'Error'])
            
            for result in results:
                writer.writerow([
                    result['bank'],
                    result['url'],
                    result.get('status', 'unknown'),
                    len(result.get('news', [])),
                    len(result.get('campaigns', [])),
                    len(result.get('updates', [])),
                    result.get('error', '')[:100]  # Truncate long errors
                ])
    
    return json_path, csv_path if format == 'both' else json_path

def main():
    scraper = BankScraper()
    cosmos_client = CosmosDBClient()  # Initialize Cosmos DB client
    results = []
    
    print("Starting enhanced Tunisian bank scraping with direct news URLs...")
    print(f"Total banks: {len(BANKS)}")
    print("=" * 80)
    
    successful_banks = 0
    
    for i, bank in enumerate(BANKS, 1):
        print(f"\n[{i}/{len(BANKS)}] Processing: {bank['name']}")
        print(f"URL: {bank['url']}")
        print(f"Language: {bank.get('language', 'unknown')}")
        
        if bank.get('skip_ssl', False):
            print("⚠️  SSL verification disabled for this bank")
        if bank.get('timeout_extended', False):
            print("⏰ Extended timeout enabled for this bank")
        if bank.get('specific_page', False):
            print("📰 Direct news/campaign page")
        
        try:
            data = scraper.scrape(bank)
            
            result = {
                "bank": bank["name"],
                "url": bank["url"],
                "language": bank.get("language", ""),
                "status": "success" if (data.get("news") or data.get("campaigns") or data.get("updates")) else "partial",
                "timestamp": datetime.now().isoformat(),
                **data
            }
            
            results.append(result)
            
            # Save to Cosmos DB immediately
            cosmos_client.save_result(result)
            
            # Print summary
            news_count = len(data.get("news", []))
            campaigns_count = len(data.get("campaigns", []))
            updates_count = len(data.get("updates", []))
            
            if result["status"] == "success":
                status = "✅ SUCCESS"
                successful_banks += 1
            else:
                status = "⚠️ PARTIAL" if news_count + campaigns_count + updates_count > 0 else "❌ FAILED"
            
            print(f"Result: {status} - {news_count} news, {campaigns_count} campaigns, {updates_count} updates")
            
            if "error" in data:
                print(f"Error: {data['error'][:80]}...")
                
            # Save intermediate results every 3 banks to prevent data loss
            if i % 3 == 0:
                save_results(results, 'json')
                print("💾 Auto-saved progress...")
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR processing {bank['name']}: {e}")
            error_result = {
                "bank": bank['name'],
                "url": bank['url'],
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "news": [],
                "campaigns": [],
                "updates": [],
                "error": f"Critical error: {str(e)}"
            }
            results.append(error_result)
            # Save error result to Cosmos DB too
            cosmos_client.save_result(error_result)

    scraper.close()
    
    # Save final results to local files
    json_path, csv_path = save_results(results, 'both')
    
    # Generate comprehensive summary
    success_count = sum(1 for r in results if r["status"] == "success")
    partial_count = sum(1 for r in results if r["status"] == "partial")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    
    total_news = sum(len(r.get("news", [])) for r in results)
    total_campaigns = sum(len(r.get("campaigns", [])) for r in results)
    total_updates = sum(len(r.get("updates", [])) for r in results)
    
    print(f"\n{'='*80}")
    print("SCRAPING COMPLETED - ENHANCED WITH DIRECT URLS")
    print(f"{'='*80}")
    print(f"Successful: {success_count}/{len(BANKS)} banks")
    print(f"Partial: {partial_count}/{len(BANKS)} banks")
    print(f"Failed: {failed_count}/{len(BANKS)} banks")
    print(f"Total news: {total_news}")
    print(f"Total campaigns: {total_campaigns}")
    print(f"Total updates: {total_updates}")
    print(f"JSON results: {json_path}")
    print(f"CSV results: {csv_path}")
    
    # Print failed banks for debugging
    if failed_count > 0:
        print(f"\nFailed banks:")
        for result in results:
            if result["status"] == "failed":
                print(f"  - {result['bank']}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()