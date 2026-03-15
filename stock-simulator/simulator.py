#!/usr/bin/env python3
"""
虚拟股票交易模拟器
实时数据通过搜索获取
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

DATA_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")

class StockSimulator:
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载投资组合数据"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._init_portfolio()
    
    def _save_data(self):
        """保存投资组合数据"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _init_portfolio(self) -> Dict:
        """初始化投资组合"""
        return {
            "initial_capital": 100000,
            "cash": 100000,
            "holdings": {},
            "transactions": [],
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
    
    def get_portfolio(self) -> Dict:
        """获取当前投资组合状态"""
        return {
            "cash": self.data["cash"],
            "holdings": self.data["holdings"],
            "total_transactions": len(self.data["transactions"])
        }
    
    def buy(self, symbol: str, name: str, price: float, shares: int) -> Dict:
        """
        买入股票
        
        Args:
            symbol: 股票代码 (如 "000001.SZ")
            name: 股票名称
            price: 买入价格
            shares: 买入股数 (100的倍数)
        
        Returns:
            交易结果
        """
        if shares % 100 != 0:
            return {"success": False, "error": "买入股数必须是100的倍数"}
        
        if shares < 100:
            return {"success": False, "error": "最少买入100股"}
        
        total_cost = price * shares
        fee = max(total_cost * 0.0003, 5)  # 佣金，最低5元
        total_cost_with_fee = total_cost + fee
        
        if total_cost_with_fee > self.data["cash"]:
            return {
                "success": False, 
                "error": f"资金不足。需要 {total_cost_with_fee:.2f}，可用 {self.data['cash']:.2f}"
            }
        
        # 执行买入
        self.data["cash"] -= total_cost_with_fee
        
        if symbol in self.data["holdings"]:
            # 更新持仓
            holding = self.data["holdings"][symbol]
            total_shares = holding["shares"] + shares
            avg_price = (holding["avg_price"] * holding["shares"] + price * shares) / total_shares
            holding["shares"] = total_shares
            holding["avg_price"] = round(avg_price, 2)
        else:
            # 新建持仓
            self.data["holdings"][symbol] = {
                "name": name,
                "shares": shares,
                "avg_price": round(price, 2)
            }
        
        # 记录交易
        transaction = {
            "type": "BUY",
            "symbol": symbol,
            "name": name,
            "price": price,
            "shares": shares,
            "fee": round(fee, 2),
            "total": round(total_cost_with_fee, 2),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["transactions"].append(transaction)
        self._save_data()
        
        return {
            "success": True,
            "transaction": transaction,
            "remaining_cash": round(self.data["cash"], 2)
        }
    
    def sell(self, symbol: str, price: float, shares: int) -> Dict:
        """
        卖出股票
        
        Args:
            symbol: 股票代码
            price: 卖出价格
            shares: 卖出股数 (100的倍数)
        
        Returns:
            交易结果
        """
        if symbol not in self.data["holdings"]:
            return {"success": False, "error": f"未持有股票 {symbol}"}
        
        holding = self.data["holdings"][symbol]
        
        if shares % 100 != 0:
            return {"success": False, "error": "卖出股数必须是100的倍数"}
        
        if shares > holding["shares"]:
            return {
                "success": False, 
                "error": f"持仓不足。持有 {holding['shares']} 股，尝试卖出 {shares} 股"
            }
        
        total_revenue = price * shares
        fee = max(total_revenue * 0.0003, 5)  # 佣金
        stamp_duty = total_revenue * 0.001  # 印花税
        total_revenue_after_fee = total_revenue - fee - stamp_duty
        
        # 计算盈亏
        cost = holding["avg_price"] * shares
        profit = total_revenue_after_fee - cost
        profit_pct = (profit / cost) * 100
        
        # 执行卖出
        self.data["cash"] += total_revenue_after_fee
        holding["shares"] -= shares
        
        if holding["shares"] == 0:
            del self.data["holdings"][symbol]
        
        # 记录交易
        transaction = {
            "type": "SELL",
            "symbol": symbol,
            "name": holding["name"],
            "price": price,
            "shares": shares,
            "fee": round(fee, 2),
            "stamp_duty": round(stamp_duty, 2),
            "total": round(total_revenue_after_fee, 2),
            "profit": round(profit, 2),
            "profit_pct": round(profit_pct, 2),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["transactions"].append(transaction)
        self._save_data()
        
        return {
            "success": True,
            "transaction": transaction,
            "profit": round(profit, 2),
            "profit_pct": round(profit_pct, 2),
            "current_cash": round(self.data["cash"], 2)
        }
    
    def get_report(self, current_prices: Dict[str, float]) -> Dict:
        """
        生成投资组合报告
        
        Args:
            current_prices: 当前股价 {symbol: price}
        
        Returns:
            投资组合报告
        """
        holdings_value = 0
        holdings_detail = []
        
        for symbol, holding in self.data["holdings"].items():
            current_price = current_prices.get(symbol, holding["avg_price"])
            market_value = current_price * holding["shares"]
            cost = holding["avg_price"] * holding["shares"]
            unrealized_profit = market_value - cost
            unrealized_profit_pct = (unrealized_profit / cost) * 100 if cost > 0 else 0
            
            holdings_value += market_value
            holdings_detail.append({
                "symbol": symbol,
                "name": holding["name"],
                "shares": holding["shares"],
                "avg_price": holding["avg_price"],
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "unrealized_profit": round(unrealized_profit, 2),
                "unrealized_profit_pct": round(unrealized_profit_pct, 2)
            })
        
        total_value = self.data["cash"] + holdings_value
        initial = self.data["initial_capital"]
        total_return = total_value - initial
        total_return_pct = (total_return / initial) * 100
        
        # 计算已实现盈亏
        realized_profit = sum(
            t.get("profit", 0) for t in self.data["transactions"] if t["type"] == "SELL"
        )
        
        return {
            "cash": round(self.data["cash"], 2),
            "holdings_value": round(holdings_value, 2),
            "total_value": round(total_value, 2),
            "initial_capital": initial,
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "realized_profit": round(realized_profit, 2),
            "unrealized_profit": round(total_return - realized_profit, 2),
            "holdings": holdings_detail,
            "transaction_count": len(self.data["transactions"])
        }
    
    def get_transactions(self, limit: int = 20) -> List[Dict]:
        """获取交易记录"""
        return self.data["transactions"][-limit:]
    
    def reset(self):
        """重置投资组合"""
        self.data = self._init_portfolio()
        self._save_data()
        return {"success": True, "message": "投资组合已重置"}


if __name__ == "__main__":
    # 测试
    sim = StockSimulator()
    print("虚拟股票交易模拟器已启动")
    print(f"初始资金: {sim.data['initial_capital']}")
    print(f"当前现金: {sim.data['cash']}")