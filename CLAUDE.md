# Sub-Agent List

This is a list and overview of sub-agents implemented in this project.

## 1. requirement-analyzer
Requirements understanding and decomposition sub-agent. Analyzes user requirements and breaks them down into implementable steps.

- Organization of functional and non-functional requirements
- Clarification of constraints and prerequisites
- Definition of implementation scope

## 2. development-designer
Development design sub-agent. Performs technical design and determines implementation approaches.

- Architecture design
- Technology stack selection
- Data model and API design

## 3. code-duplication-detector
Code duplication detection sub-agent. Proposes opportunities to utilize existing code and promotes DRY principles.

- Existing code utilization proposals during design phase (1st time)
- Code duplication detection after implementation (2nd time)
- Proposals for common code extraction and refactoring

## 4. design-docs-creator
Design documentation creation sub-agent. Creates comprehensive design documents.

- Creation of detailed design documents
- Development of implementation plans (division into implementation units)
- Planning of PR division strategy
- Detailed specifications at a level where implementers won't get confused

## 5. implementation-agent
Implementation sub-agent. Performs reliable step-by-step implementation based on design docs.

- Implementation following design docs
- Implementation by units (300-500 lines each)
- Frontend and backend implementation

## 6. implementation-validator
Implementation validation sub-agent. Validates implementation completeness and quality step by step.

- Detection of TODO/FIXME comments
- Detection of mock implementations
- Discovery of unimplemented functions and empty implementations
- Detection of hardcoded values
- Step-by-step quality assurance

## 7. code-reviewer
Code review sub-agent. Checks the quality of implemented code and provides improvement suggestions.

- Code quality evaluation
- Security checks
- Performance optimization suggestions
- Best practices verification

## 8. test-agent
Test sub-agent. Confirms that all quality assurance checks pass.

- Unit test execution
- Integration test execution
- Coverage measurement
- Test result reporting

## 9. playwright-mcp-verifier
UI operation verification sub-agent. Performs UI operation verification using Playwright MCP.

- E2E test execution
- Automated UI operation verification
- Environment error detection
- Operation verification report generation

## Sub-Agent Usage Rules

1. **Invocation Authority**: Only the main orchestrator can invoke sub-agents
2. **Inter-Agent Invocation Prohibition**: Direct invocation between sub-agents is not allowed
3. **Task Tool Usage**: All sub-agent invocations must use the Task tool
4. **Chart Creation**: All sub-agents must use Mermaid.js to create charts and diagrams