#!/usr/bin/env node

/**
 * Frontend Testing Script
 * Tests deployed frontend functionality and API integration
 */

const puppeteer = require("puppeteer");
const axios = require("axios");

class FrontendTester {
  constructor(frontendUrl, backendUrl) {
    this.frontendUrl = frontendUrl.replace(/\/$/, ""); // Remove trailing slash
    this.backendUrl = backendUrl.replace(/\/$/, "");
    this.browser = null;
    this.page = null;
  }

  async setup() {
    console.log("🚀 Setting up browser...");
    this.browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });
    this.page = await this.browser.newPage();

    // Set viewport
    await this.page.setViewport({ width: 1280, height: 720 });

    // Enable console logging
    this.page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log("❌ Browser Console Error:", msg.text());
      }
    });

    // Enable error logging
    this.page.on("pageerror", (error) => {
      console.log("❌ Page Error:", error.message);
    });
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async testPageLoad() {
    console.log("\n📄 Testing page load...");

    try {
      const response = await this.page.goto(this.frontendUrl, {
        waitUntil: "networkidle0",
        timeout: 30000,
      });

      if (response.ok()) {
        console.log("✅ Page loaded successfully");

        // Check if React app loaded
        const title = await this.page.title();
        console.log(`   Title: ${title}`);

        // Check for React root
        const reactRoot = await this.page.$("#root");
        if (reactRoot) {
          console.log("✅ React app mounted");
        } else {
          console.log("❌ React app not found");
          return false;
        }

        return true;
      } else {
        console.log(`❌ Page load failed: ${response.status()}`);
        return false;
      }
    } catch (error) {
      console.log(`❌ Page load error: ${error.message}`);
      return false;
    }
  }

  async testEnvironmentVariables() {
    console.log("\n🔧 Testing environment variables...");

    try {
      const apiUrl = await this.page.evaluate(() => {
        return window.process?.env?.REACT_APP_API_URL || "Not found";
      });

      const environment = await this.page.evaluate(() => {
        return window.process?.env?.REACT_APP_ENVIRONMENT || "Not found";
      });

      console.log(`   API URL: ${apiUrl}`);
      console.log(`   Environment: ${environment}`);

      if (apiUrl === "Not found") {
        console.log(
          "⚠️ Environment variables not accessible (this is normal in production builds)"
        );
        return true; // This is actually expected in production
      }

      return true;
    } catch (error) {
      console.log(`❌ Environment variable test error: ${error.message}`);
      return false;
    }
  }

  async testAPIConnection() {
    console.log("\n🔌 Testing API connection...");

    try {
      // Test if frontend can reach backend
      const healthResponse = await axios.get(`${this.backendUrl}/health`, {
        timeout: 10000,
      });

      if (healthResponse.status === 200) {
        console.log("✅ Backend API is reachable");
        console.log(`   Status: ${healthResponse.data.status}`);
        return true;
      } else {
        console.log(`❌ Backend API returned: ${healthResponse.status}`);
        return false;
      }
    } catch (error) {
      console.log(`❌ API connection error: ${error.message}`);
      return false;
    }
  }

  async testNavigation() {
    console.log("\n🧭 Testing navigation...");

    try {
      // Wait for page to load
      await this.page.waitForSelector("body", { timeout: 10000 });

      // Look for navigation elements
      const navElements = await this.page.$$('nav, .nav, [role="navigation"]');
      if (navElements.length > 0) {
        console.log("✅ Navigation elements found");
      } else {
        console.log("⚠️ No navigation elements found");
      }

      // Test if we can find common UI elements
      const commonElements = ["button", "input", "form", "a[href]"];

      for (const selector of commonElements) {
        const elements = await this.page.$$(selector);
        if (elements.length > 0) {
          console.log(`✅ Found ${elements.length} ${selector} elements`);
        }
      }

      return true;
    } catch (error) {
      console.log(`❌ Navigation test error: ${error.message}`);
      return false;
    }
  }

  async testResponsiveDesign() {
    console.log("\n📱 Testing responsive design...");

    try {
      const viewports = [
        { width: 1920, height: 1080, name: "Desktop" },
        { width: 768, height: 1024, name: "Tablet" },
        { width: 375, height: 667, name: "Mobile" },
      ];

      for (const viewport of viewports) {
        await this.page.setViewport(viewport);
        await this.page.waitForTimeout(1000); // Wait for layout

        const bodyVisible = await this.page.$eval("body", (el) => {
          const rect = el.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0;
        });

        if (bodyVisible) {
          console.log(
            `✅ ${viewport.name} (${viewport.width}x${viewport.height}) renders correctly`
          );
        } else {
          console.log(`❌ ${viewport.name} rendering issue`);
        }
      }

      // Reset to desktop
      await this.page.setViewport({ width: 1280, height: 720 });

      return true;
    } catch (error) {
      console.log(`❌ Responsive design test error: ${error.message}`);
      return false;
    }
  }

  async testFormElements() {
    console.log("\n📝 Testing form elements...");

    try {
      // Look for forms
      const forms = await this.page.$$("form");
      console.log(`   Found ${forms.length} forms`);

      // Look for inputs
      const inputs = await this.page.$$("input");
      console.log(`   Found ${inputs.length} input fields`);

      // Look for buttons
      const buttons = await this.page.$$("button");
      console.log(`   Found ${buttons.length} buttons`);

      if (forms.length > 0 || inputs.length > 0 || buttons.length > 0) {
        console.log("✅ Interactive elements found");
        return true;
      } else {
        console.log("⚠️ No interactive elements found");
        return true; // Not necessarily an error
      }
    } catch (error) {
      console.log(`❌ Form elements test error: ${error.message}`);
      return false;
    }
  }

  async testPerformance() {
    console.log("\n⚡ Testing performance...");

    try {
      const startTime = Date.now();

      await this.page.goto(this.frontendUrl, {
        waitUntil: "networkidle0",
        timeout: 30000,
      });

      const loadTime = Date.now() - startTime;
      console.log(`   Page load time: ${loadTime}ms`);

      if (loadTime < 3000) {
        console.log("✅ Fast loading time");
      } else if (loadTime < 5000) {
        console.log("⚠️ Moderate loading time");
      } else {
        console.log("❌ Slow loading time");
      }

      // Check for performance metrics
      const performanceMetrics = await this.page.evaluate(() => {
        const navigation = performance.getEntriesByType("navigation")[0];
        return {
          domContentLoaded:
            navigation.domContentLoadedEventEnd -
            navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        };
      });

      console.log(
        `   DOM Content Loaded: ${performanceMetrics.domContentLoaded}ms`
      );
      console.log(`   Load Complete: ${performanceMetrics.loadComplete}ms`);

      return true;
    } catch (error) {
      console.log(`❌ Performance test error: ${error.message}`);
      return false;
    }
  }

  async runAllTests() {
    console.log(`🧪 Starting frontend tests for: ${this.frontendUrl}`);
    console.log(`🔗 Backend API: ${this.backendUrl}`);

    const tests = [
      { name: "Page Load", test: () => this.testPageLoad() },
      {
        name: "Environment Variables",
        test: () => this.testEnvironmentVariables(),
      },
      { name: "API Connection", test: () => this.testAPIConnection() },
      { name: "Navigation", test: () => this.testNavigation() },
      { name: "Responsive Design", test: () => this.testResponsiveDesign() },
      { name: "Form Elements", test: () => this.testFormElements() },
      { name: "Performance", test: () => this.testPerformance() },
    ];

    let passed = 0;
    let failed = 0;

    for (const { name, test } of tests) {
      console.log(`\n--- Running: ${name} ---`);
      try {
        const result = await test();
        if (result) {
          passed++;
        } else {
          failed++;
        }
      } catch (error) {
        console.log(`❌ Test ${name} crashed: ${error.message}`);
        failed++;
      }
    }

    // Results
    const total = passed + failed;
    console.log(`\n${"=".repeat(50)}`);
    console.log("FRONTEND TEST RESULTS");
    console.log(`${"=".repeat(50)}`);
    console.log(`Total tests: ${total}`);
    console.log(`Passed: ${passed} ✅`);
    console.log(`Failed: ${failed} ❌`);
    console.log(`Success rate: ${((passed / total) * 100).toFixed(1)}%`);
    console.log(`${"=".repeat(50)}`);

    return failed === 0;
  }
}

async function main() {
  const frontendUrl = process.argv[2] || process.env.FRONTEND_URL;
  const backendUrl =
    process.argv[3] || process.env.REACT_APP_API_URL || process.env.BACKEND_URL;

  if (!frontendUrl) {
    console.error("❌ Frontend URL not provided");
    console.log("Usage: node test_frontend.js <frontend_url> [backend_url]");
    console.log("   or: FRONTEND_URL=<url> node test_frontend.js");
    process.exit(1);
  }

  if (!backendUrl) {
    console.error("❌ Backend URL not provided");
    console.log("Usage: node test_frontend.js <frontend_url> <backend_url>");
    process.exit(1);
  }

  const tester = new FrontendTester(frontendUrl, backendUrl);

  try {
    await tester.setup();
    const success = await tester.runAllTests();

    if (success) {
      console.log("\n🎉 All frontend tests passed!");
      process.exit(0);
    } else {
      console.log("\n💥 Some frontend tests failed!");
      process.exit(1);
    }
  } catch (error) {
    console.error("❌ Test suite crashed:", error.message);
    process.exit(1);
  } finally {
    await tester.cleanup();
  }
}

// Handle uncaught exceptions
process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
  process.exit(1);
});

if (require.main === module) {
  main();
}
