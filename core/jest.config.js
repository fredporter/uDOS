export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>', '<rootDir>/../memory/tests', '<rootDir>/memory/tests'],
  testMatch: ['**/__tests__/**/*.test.ts', '<rootDir>/../memory/tests/**/*.test.ts', '<rootDir>/memory/tests/**/*.test.ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 60,
      lines: 60,
      statements: 60,
    },
  },
  extensionsToTreatAsEsm: ['.ts'],
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
    '^marked$': '<rootDir>/__mocks__/marked.js',
  },
  testPathIgnorePatterns: [
    'memory/tests/legacy/.*',
    '\\.\\!\\d+\\!tile-compositor\\.test\\.ts$',
  ],
  transformIgnorePatterns: [
    'node_modules/(?!(marked)/)',
  ],
}
