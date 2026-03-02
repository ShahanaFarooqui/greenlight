module.exports = {
  preset: "ts-jest/presets/default-esm",
  testEnvironment: "node",
  maxWorkers: 1,
  testTimeout: 120_000, // GL node ops can be slow; 120 s is safer than 30 s
  runner: "jest-runner",
  resetModules: true,
  restoreMocks: true,
  clearMocks: true,
  extensionsToTreatAsEsm: [".ts"],
  transform: {
    "^.+\\.ts$": [
      "ts-jest",
      { useESM: true },
    ],
  },
  moduleNameMapper: {
    "^(\\.{1,2}/.*)\\.js$": "$1",
  },
  // globalSetup: "./jest.globalSetup.ts",
  // Run setup_network.py before any tests
  globalSetup: "<rootDir>/tests/globalSetup.ts",

  // Kill all network processes after all tests
  globalTeardown: "<rootDir>/tests/globalTeardown.ts",

  testMatch: ["<rootDir>/tests/**/*.spec.ts"],
  testEnvironment: '<rootDir>/tests/GltestEnvironment.ts',
};
