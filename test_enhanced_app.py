#!/usr/bin/env python3
"""
Test script for the enhanced IPC Crime Analyzer
"""

import requests
import json
import time

def test_enhanced_system():
    """Test the enhanced system endpoints"""
    
    base_url = "http://localhost:5001"
    
    print("=" * 60)
    print("ENHANCED IPC CRIME ANALYZER - SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Check system status
    print("\n🔍 Testing System Status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ System Status:")
            print(f"   Enhanced System Available: {status['enhanced_system']['available']}")
            print(f"   System Version: {status['enhanced_system']['version']}")
            print(f"   Accuracy Improvement: {status['enhanced_system']['accuracy_improvement']}")
            print(f"   Features: {list(status['enhanced_system']['features'].keys())}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 2: Test crime analysis
    test_cases = [
        "Someone stole my phone",
        "A person hit me with a stick during an argument",
        "Someone threatened me with a knife",
        "A person broke into my house and stole my laptop"
    ]
    
    print(f"\n🔍 Testing Crime Analysis ({len(test_cases)} cases)...")
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. Query: \"{query}\"")
        try:
            response = requests.post(f"{base_url}/api/analyze", 
                                   json={"description": query})
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Analysis successful")
                print(f"   System Version: {result.get('system_version', 'Unknown')}")
                print(f"   Confidence: {result.get('confidence', 0):.1%}")
                
                if result.get('sections'):
                    sections = result['sections']
                    print(f"   Found {len(sections)} relevant sections:")
                    for j, section in enumerate(sections[:3], 1):
                        print(f"      {j}. IPC {section['section_number']} - {section['title']} (Score: {section['score']:.3f})")
                else:
                    print("   No relevant sections found")
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
    
    # Test 3: Test enhanced system endpoint
    print(f"\n🔍 Testing Enhanced System Endpoint...")
    try:
        response = requests.post(f"{base_url}/api/test-enhanced", 
                               json={"queries": test_cases[:2]})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced system test successful")
            print(f"   Enhanced System Available: {result['enhanced_system_available']}")
            print(f"   Total Tests: {result['total_tests']}")
            
            for test_result in result['test_results']:
                print(f"   Query: \"{test_result['query']}\"")
                print(f"   System: {test_result['system_used']}")
                print(f"   Confidence: {test_result['confidence']:.1%}")
                print(f"   Sections: {test_result['sections']}")
        else:
            print(f"❌ Enhanced system test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced system test error: {e}")
    
    print(f"\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Enhanced IPC Crime Analyzer Test...")
    print("Note: Make sure the Flask app is running on http://localhost:5001")
    print("Run: python app.py")
    print()
    
    # Wait a moment for user to start the app
    time.sleep(2)
    
    test_enhanced_system()
