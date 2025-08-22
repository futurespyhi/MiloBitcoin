#!/usr/bin/env python3
# Test script for Milo Bitcoin data collection

import asyncio
import sys
import os

# Add parent directory to path for importing main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from milo_bitcoin_main import BitcoinDataCollector, BitcoinMetrics

async def test_individual_apis():
    """Test each API individually"""
    print("🧪 Testing individual APIs...\n")
    
    collector = BitcoinDataCollector()
    
    try:
        # Test 1: CoinGecko (Price data)
        print("1️⃣ Testing CoinGecko API (Price data)...")
        price_data = await collector.get_bitcoin_price_data()
        if price_data and 'bitcoin' in price_data:
            btc = price_data['bitcoin']
            print(f"   ✅ Success! Price: ${btc.get('usd', 'N/A'):,}")
            print(f"   📊 Market Cap: ${btc.get('usd_market_cap', 'N/A'):,}")
        else:
            print("   ❌ Failed to get price data")
        
        print()
        
        # Test 2: Blockchain.info (On-chain data)
        print("2️⃣ Testing Blockchain.info API (On-chain data)...")
        onchain_data = await collector.get_on_chain_metrics()
        if onchain_data:
            print(f"   ✅ Success! Transactions: {onchain_data.get('n_tx', 'N/A'):,}")
            print(f"   ⛓️ Hash Rate: {onchain_data.get('hash_rate', 'N/A')}")
        else:
            print("   ❌ Failed to get on-chain data")
        
        print()
        
        # Test 3: Alternative.me (Fear & Greed)
        print("3️⃣ Testing Alternative.me API (Fear & Greed Index)...")
        sentiment_data = await collector.get_fear_greed_index()
        if sentiment_data and sentiment_data.get('data'):
            fg = sentiment_data['data'][0]
            print(f"   ✅ Success! Sentiment: {fg.get('value_classification', 'N/A')} ({fg.get('value', 'N/A')}/100)")
        else:
            print("   ❌ Failed to get sentiment data")
        
        print()
        
        # Test 4: News API (optional)
        print("4️⃣ Testing NewsAPI (Bitcoin news - optional)...")
        news_data = await collector.get_bitcoin_news(limit=3)
        if news_data:
            print(f"   ✅ Success! Found {len(news_data)} articles")
            for i, article in enumerate(news_data[:2], 1):
                print(f"   📰 {i}. {article.get('title', 'No title')[:60]}...")
        else:
            print("   ⚠️ No news data (likely missing NEWS_API_KEY)")
        
    finally:
        collector.close()

async def test_comprehensive_collection():
    """Test comprehensive data collection"""
    print("\n🔄 Testing comprehensive data collection...\n")
    
    collector = BitcoinDataCollector()
    
    try:
        metrics = await collector.collect_comprehensive_data()
        
        print("📊 Comprehensive Bitcoin Data Summary:")
        print("=" * 50)
        print(f"💰 Price: ${metrics.price:,.2f}")
        print(f"📈 Market Cap: ${metrics.market_cap:,.0f}")
        print(f"📊 24h Volume: ${metrics.volume_24h:,.0f}")
        print(f"😰 Fear & Greed: {metrics.fear_greed_index}/100")
        print(f"⛓️ Hash Rate: {metrics.hash_rate}")
        print(f"💸 Transaction Count: {metrics.transaction_count:,}")
        print(f"💰 Network Fees: ${metrics.fees_usd:.2f}")
        print("=" * 50)
        
        # Validate data quality
        issues = []
        if metrics.price == 0:
            issues.append("Price data missing")
        if metrics.fear_greed_index == 50:
            issues.append("Fear & Greed might be default value")
        if metrics.transaction_count == 0:
            issues.append("Transaction count missing")
        
        if issues:
            print("⚠️ Data quality issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ All data looks good!")
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
    finally:
        collector.close()

async def main():
    """Main test function"""
    print("🐱₿ Milo Bitcoin Data Collection Test")
    print("=" * 50)
    print("Testing APIs without requiring API keys...")
    print("(CoinGecko, Blockchain.info, Alternative.me are free)\n")
    
    # Check environment
    print("🔍 Environment Check:")
    env_vars = ['NEWS_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Not set"
        print(f"   {var}: {status}")
    print()
    
    # Run tests
    await test_individual_apis()
    await test_comprehensive_collection()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
