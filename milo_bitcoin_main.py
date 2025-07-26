# Milo_Bitcoin 🐱₿
# Conversational Bitcoin Analysis Assistant with RAG + LLM
# The first AI cat to understand Bitcoin! - Created by Norton Gu

import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import requests
from dataclasses import dataclass

@dataclass
class BitcoinMetrics:
    """Bitcoin核心指标数据结构"""
    price: float
    market_cap: float
    volume_24h: float
    hash_rate: float
    fear_greed_index: int
    active_addresses: int
    transaction_count: int
    fees_usd: float

class BitcoinDataCollector:
    """专门收集Bitcoin相关数据"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.blockchain_info_api = "https://api.blockchain.info/stats"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
    async def get_bitcoin_price_data(self) -> Dict:
        """获取Bitcoin价格和市场数据"""
        try:
            url = f"{self.coingecko_api}/simple/price"
            params = {
                'ids': 'bitcoin',
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            response = requests.get(url, params=params)
            print("📈 Milo fetched Bitcoin price data")
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching price data: {e}")
            return {}
    
    async def get_on_chain_metrics(self) -> Dict:
        """获取链上数据"""
        try:
            response = requests.get(self.blockchain_info_api)
            print("⛓️ Milo fetched on-chain metrics")
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching on-chain data: {e}")
            return {}
    
    async def get_fear_greed_index(self) -> Dict:
        """获取恐慌贪婪指数"""
        try:
            response = requests.get(f"{self.fear_greed_api}?limit=1")
            print("😰 Milo checked market sentiment")
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching fear/greed index: {e}")
            return {}
    
    async def get_bitcoin_news(self, limit: int = 10) -> List[Dict]:
        """获取Bitcoin相关新闻"""
        try:
            if not self.news_api_key:
                print("⚠️ No News API key found")
                return []
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': 'bitcoin OR BTC',
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit
            }
            response = requests.get(url, params=params)
            print(f"🗞️ Milo collected {limit} Bitcoin news articles")
            return response.json().get('articles', [])
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            return []
    
    async def collect_comprehensive_data(self) -> BitcoinMetrics:
        """收集综合Bitcoin数据"""
        print("🔄 Milo is collecting comprehensive Bitcoin data...")
        
        # 并行获取所有数据
        price_data, on_chain_data, sentiment_data, news_data = await asyncio.gather(
            self.get_bitcoin_price_data(),
            self.get_on_chain_metrics(),
            self.get_fear_greed_index(),
            self.get_bitcoin_news()
        )
        
        # 解析数据
        bitcoin_price = price_data.get('bitcoin', {})
        fear_greed = sentiment_data.get('data', [{}])[0] if sentiment_data.get('data') else {}
        
        metrics = BitcoinMetrics(
            price=bitcoin_price.get('usd', 0),
            market_cap=bitcoin_price.get('usd_market_cap', 0),
            volume_24h=bitcoin_price.get('usd_24h_vol', 0),
            hash_rate=on_chain_data.get('hash_rate', 0),
            fear_greed_index=int(fear_greed.get('value', 50)),
            active_addresses=on_chain_data.get('n_btc_discovered', 0),
            transaction_count=on_chain_data.get('n_tx', 0),
            fees_usd=on_chain_data.get('total_fees_btc', 0) * bitcoin_price.get('usd', 0)
        )
        
        print("✅ Milo gathered all Bitcoin data successfully!")
        return metrics

class BitcoinRAGSystem:
    """Bitcoin专用RAG系统"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self.bitcoin_knowledge_base = []
        
    def load_bitcoin_knowledge(self):
        """加载Bitcoin基础知识库"""
        knowledge_sources = [
            "Bitcoin Whitepaper by Satoshi Nakamoto",
            "Technical analysis indicators for Bitcoin",
            "Bitcoin halving events and market cycles", 
            "Lightning Network and layer 2 solutions",
            "Bitcoin mining and hash rate fundamentals",
            "DeFi and Bitcoin ecosystem development"
        ]
        
        print("📚 Milo is loading Bitcoin knowledge base...")
        self.bitcoin_knowledge_base = knowledge_sources
        return knowledge_sources
        
    def build_knowledge_base(self, documents: List[str]):
        """构建Bitcoin专用知识库"""
        print("🔨 Milo is building Bitcoin knowledge base...")
        # TODO: 实现向量数据库构建
        # 将包含：Bitcoin白皮书、技术分析、市场周期、挖矿知识等
        
    def retrieve_bitcoin_context(self, query: str, metrics: BitcoinMetrics) -> str:
        """检索Bitcoin相关上下文"""
        print(f"🔍 Milo is searching Bitcoin knowledge for: {query}")
        
        # 基于当前数据构建上下文
        context = f"""
Current Bitcoin Data:
- Price: ${metrics.price:,.2f}
- Market Cap: ${metrics.market_cap:,.0f}
- 24h Volume: ${metrics.volume_24h:,.0f}
- Fear & Greed Index: {metrics.fear_greed_index}/100
- Hash Rate: {metrics.hash_rate}
- Daily Transactions: {metrics.transaction_count:,}

Market Analysis Context:
- Current market sentiment: {'Extreme Fear' if metrics.fear_greed_index < 25 else 'Fear' if metrics.fear_greed_index < 45 else 'Neutral' if metrics.fear_greed_index < 55 else 'Greed' if metrics.fear_greed_index < 75 else 'Extreme Greed'}
- Network activity: {'High' if metrics.transaction_count > 300000 else 'Medium' if metrics.transaction_count > 200000 else 'Low'}
"""
        return context

class MiloBitcoinLLM:
    """Milo的Bitcoin专用LLM系统"""
    
    def __init__(self):
        self.model = None  # TODO: 加载微调后的Bitcoin专用模型
        self.system_prompt = self._create_bitcoin_system_prompt()
        
    def _create_bitcoin_system_prompt(self) -> str:
        """创建Bitcoin专用系统提示"""
        return """You are Milo 🐱₿, a knowledgeable and friendly Bitcoin analysis cat.

Your expertise includes:
- Bitcoin fundamentals and blockchain technology
- Technical analysis and market trends  
- On-chain metrics and their implications
- Risk assessment and educational guidance
- Market sentiment analysis

Your personality:
- Friendly and approachable, but professional
- Always emphasize education over speculation
- Include appropriate risk warnings
- Use cat emojis occasionally 🐾
- Explain complex concepts in simple terms

IMPORTANT DISCLAIMERS:
- You provide educational analysis, NOT financial advice
- Always remind users to do their own research
- Emphasize the high-risk nature of cryptocurrency investments
- Never guarantee returns or price predictions

Remember: You're here to educate and inform, not to encourage reckless investment!
"""
    
    def analyze_bitcoin_query(self, user_query: str, context: str, metrics: BitcoinMetrics) -> str:
        """分析用户的Bitcoin相关问题"""
        print("🧠 Milo is analyzing your Bitcoin question...")
        
        # TODO: 实现LLM推理
        # 这里将使用微调后的模型结合实时数据和上下文
        
        # 临时回复逻辑
        if "price" in user_query.lower():
            return f"""🐱 Current Bitcoin price is ${metrics.price:,.2f}! 

Based on the data I'm seeing:
- Market sentiment is {'quite fearful' if metrics.fear_greed_index < 50 else 'optimistic'} (Fear & Greed: {metrics.fear_greed_index}/100)
- Network activity shows {metrics.transaction_count:,} transactions today
- 24h trading volume: ${metrics.volume_24h:,.0f}

Remember: Past performance doesn't predict future results! 🐾
*This is educational analysis, not financial advice. Always DYOR!*"""
        
        elif "should i buy" in user_query.lower() or "investment" in user_query.lower():
            return """🐱 I can't give investment advice, but I can help you understand Bitcoin better! 

Key things to consider:
- Only invest what you can afford to lose completely
- Understand the technology and use cases
- Consider dollar-cost averaging instead of lump sum
- Learn about proper wallet security

Want me to explain any specific aspect of Bitcoin? 🐾
*Always do your own research and consult financial advisors!*"""
        
        else:
            return f"""🐱 That's an interesting Bitcoin question! 

Based on current market data:
{context}

I'm still learning to provide more detailed analysis. What specific aspect of Bitcoin would you like to explore? 🐾

*Educational purposes only - not financial advice!*"""

class MiloBitcoinAssistant:
    """Milo Bitcoin助手主类"""
    
    def __init__(self):
        self.data_collector = BitcoinDataCollector()
        self.rag_system = BitcoinRAGSystem()
        self.llm = MiloBitcoinLLM()
        self.current_metrics = None
        print("🐱₿ Milo Bitcoin Assistant initialized! Ready to talk Bitcoin!")
        
    async def refresh_data(self):
        """刷新Bitcoin数据"""
        print("🔄 Milo is refreshing Bitcoin data...")
        self.current_metrics = await self.data_collector.collect_comprehensive_data()
        
    async def chat(self, user_question: str) -> str:
        """与用户进行Bitcoin对话"""
        print(f"💬 User: {user_question}")
        
        # 确保有最新数据
        if not self.current_metrics:
            await self.refresh_data()
        
        # 获取相关上下文
        context = self.rag_system.retrieve_bitcoin_context(user_question, self.current_metrics)
        
        # LLM分析和回复
        response = self.llm.analyze_bitcoin_query(user_question, context, self.current_metrics)
        
        return response
    
    async def get_market_summary(self) -> str:
        """获取Bitcoin市场摘要"""
        print("📊 Milo is preparing Bitcoin market summary...")
        
        if not self.current_metrics:
            await self.refresh_data()
        
        summary = f"""🐱₿ Milo's Bitcoin Market Summary

💰 Price: ${self.current_metrics.price:,.2f}
📊 Market Cap: ${self.current_metrics.market_cap:,.0f}
📈 24h Volume: ${self.current_metrics.volume_24h:,.0f}
😰 Fear & Greed: {self.current_metrics.fear_greed_index}/100
⛓️ Hash Rate: {self.current_metrics.hash_rate}
💸 Network Fees: ${self.current_metrics.fees_usd:.2f}

*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*
*For educational purposes only! 🐾*"""
        
        return summary

async def main():
    """主函数 - Milo Bitcoin Demo"""
    print("🚀 Milo Bitcoin is starting...")
    print("🐱₿" + "=" * 50)
    
    milo = MiloBitcoinAssistant()
    
    # 加载知识库
    milo.rag_system.load_bitcoin_knowledge()
    
    # Demo功能
    print("\n📊 Demo: Bitcoin Market Summary")
    summary = await milo.get_market_summary()
    print(summary)
    
    print("\n💬 Demo: Chat with Milo about Bitcoin")
    questions = [
        "What's the current Bitcoin price?",
        "Should I buy Bitcoin now?",
        "Explain Bitcoin halving to me"
    ]
    
    for question in questions:
        print(f"\n🙋 Question: {question}")
        response = await milo.chat(question)
        print(f"🐱 Milo: {response}")
        print("-" * 50)
    
    print("\n✅ Demo completed! Milo is ready for Bitcoin analysis...")
    print("🐾 *purrs while thinking about blockchain*")

if __name__ == "__main__":
    asyncio.run(main())

# Milo's Bitcoin Development Roadmap 🎯
# Week 1: Bitcoin data pipeline + Basic RAG (Milo learns Bitcoin!)
# Week 2: LLM fine-tuning + Advanced analysis (Milo becomes Bitcoin expert!)  
# Week 3: Frontend + Real-time features (Milo gets a beautiful interface!)
# Week 4: Deployment + Community feedback (Milo goes live on the internet!)