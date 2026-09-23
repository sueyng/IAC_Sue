# SEED InnerSource CloudFormation Template Update Process

## 📋 Overview
This document outlines the standardized process for updating AWS CloudFormation templates under SEED InnerSource in Azure DevOps. This process ensures consistency, quality, and proper governance for infrastructure changes while maintaining backward compatibility and following enterprise standards.

---

## 🔄 Complete Workflow Process

### Step 1: Branch Creation and Environment Setup

#### 1.1 Clone Repository Using Azure DevOps "Clone in VS Code" Feature

**Step 1: Navigate to Azure DevOps Repository**
1. **Open browser** and go to:
   ```
   https://dev.azure.com/IHIS-HIP/SEED%20InnerSource/_git/IaC-Templates
   ```
2. **Sign in** with your SEED InnerSource credentials
3. **Navigate to Files tab** in the repository

**Step 2: Use "Clone in VS Code" Button**
1. **Click "Clone" button** (top right of the Files view)
2. **Select "Clone in VS Code"** from the dropdown menu
3. **Browser will prompt:** "Open Visual Studio Code?"
4. **Click "Open Visual Studio Code"** to proceed

**Step 3: Choose Local Clone Location**
1. **VS Code will open** with a folder selection dialog
2. **Navigate to your preferred location** (e.g., `D:\Repositories\` or `D:\`)
3. **Select folder** where you want to clone (VS Code will create `IaC-Templates-8` folder automatically)
4. **Click "Select as Repository Destination"**

**Step 4: Automatic Setup**
1. **VS Code will automatically:**
   - Clone the repository into a new `IaC-Templates-8` folder
   - Open the cloned repository in VS Code
   - Configure Azure DevOps integration
   - Set up authentication if needed

**Step 5: Verify Setup**
1. **Check Explorer panel** (`Ctrl+Shift+E`) - you should see the repository structure:
   ```
   IaC-Templates-8/
   ├── AppSubsystem/
   ├── FHIRNexus/
   ├── InfraPlatform/
   ├── v1/
   ├── v2/
   ├── v3/
   └── v4/
   ```
2. **Check branch indicator** in status bar (should show "master")
3. **Verify Azure DevOps integration** - look for Azure DevOps indicators

**Step 6: Switch to Master Branch and Pull Latest** (if not already on master)
1. **Look at VS Code status bar** (bottom left) - you'll see the current branch name (like "eks-update" in your case)
2. **Click on the branch name** in the status bar
3. **Select "master"** from the dropdown list of branches
4. **Wait for VS Code to switch** to the master branch
5. **Pull latest changes:**
   - Press `Ctrl+Shift+P` and type "Git: Pull"
   - Or click the sync button (circular arrows) in the status bar
   - Select "Git: Pull" to get latest changes from master

**Step 7: Create Feature Branch**
1. **Click on "master"** in the status bar (branch indicator)
2. **Select "Create new branch..."** from the dropdown menu
3. **Enter branch name:**
   - **You can use any branch name** up to the IAC code checkin
   - **Suggested format**: `feature/[component]-v[X]-[brief-description]`
   - **Alternative formats**: `[component]-update`, `[your-name]/[feature]`, `hotfix/[issue]`
4. **Press Enter** to create and switch to the new branch
5. **VS Code status bar will update** to show your new branch name

**Branch Naming Examples (All Acceptable):**
- `feature/rds-v4-multi-az-support` (Recommended format)
- `eks-update` (Simple component update)
- `john-smith/s3-encryption` (Personal branch format)
- `hotfix/parameter-validation` (Hotfix format)
- `component-enhancement` (Generic descriptive name)
- `v6-flexible-deployment` (Version-focused name)

#### 1.2 Navigate to Target Component Directory

**Using VS Code Explorer:**
1. **Open Explorer Panel** (`Ctrl+Shift+E`)
2. **Navigate to your component folder:**
   - `InfraPlatform/eks/` (for EKS templates)
   - `InfraPlatform/rds/rdspostgres/` (for RDS PostgreSQL)
   - `AppSubsystem/BackendECS/` (for Backend ECS)
3. **Right-click on the latest version folder** (e.g., `v5` or `v6`)
4. **Note the version number** to create the next version (e.g., if latest is `v5`, create `v6`)

---

### Step 2: CloudFormation Template Updates

#### 2.1 Copy All Templates Using VS Code GUI
Even if you're only changing ONE CloudFormation template, you must copy ALL templates in the component folder to maintain version consistency.

**Example Scenario: Updating Any Component Template**

**Step 1: Copy and Rename Previous Version Folder**
1. **Navigate to your component folder** (e.g., `InfraPlatform/eks/`) in VS Code Explorer
2. **Right-click on the latest version folder** (e.g., `v5`)
3. **Select "Copy"** from the context menu
4. **Right-click in the empty space** within the component folder
5. **Select "Paste"** - VS Code will create `v5 copy`
6. **Right-click on the new `v5 copy` folder**
7. **Select "Rename"** and change it to the next version (e.g., `v6`)
8. **Press Enter** to confirm the rename

**Step 2: Verify Complete Copy**
1. **Open the new version folder** (e.g., `v6`) in Explorer
2. **Confirm ALL files are present**:
   - `cf-*.yaml` files (all CloudFormation templates)
   - `parameters-*.json` files (all parameter files)
   - `README.md`
   - `release-notes.md` (if exists)
   - Any other component-specific files

**Step 3: Verify File Structure**
```
InfraPlatform/[component]/v[X]/
├── cf-main-template.yaml (✏️ Update this with your changes)
├── cf-additional-template.yaml (📄 Copy unchanged but update version tags)
├── parameters-main.json (📝 Update parameter values)
├── parameters-additional.json (📝 Update parameter values)
└── README.md (📝 Update documentation)
```

**Why Copy All Templates?**
- Maintains version consistency across the component
- Ensures all templates in a version folder work together
- Prevents dependency conflicts between template versions
- Follows SEED InnerSource governance standards

#### 2.2 Implement Your Changes
**Example: Adding New Parameter to CloudFormation Template**

```yaml
# Add new parameter following naming convention
Parameters:
  # ... existing parameters ...
  
  NewFeatureEnabled:
    Type: String
    AllowedValues:
      - "yes"
      - "no"
    Default: "no"
    Description: "Enable new feature functionality (yes/no)"
    
  EnhancedLoggingEnabled:
    Type: String
    AllowedValues:
      - "true"
      - "false"
    Default: "false"
    Description: "Enable enhanced logging and monitoring (true/false)"
```

---

### Step 3: Parameter Naming Convention and Validation

#### 3.1 Follow Proper Naming Standards
**✅ Good Parameter Names:**
```yaml
NewFeatureEnabled              # Clear, descriptive, follows PascalCase
MultiRegionDeploymentMode      # Descriptive, indicates purpose
BackupRetentionDays            # Clear units and purpose
EncryptionKeyRotationEnabled   # Boolean indication clear
```

**❌ Avoid These Patterns:**
```yaml
Feature                        # Too vague
Flag1                          # Non-descriptive
new_param                      # Wrong case convention
existing-param-name            # Don't match existing names
```

---

### Step 4: Sandbox Environment Testing

#### 4.1 Deploy to Sandbox for Validation
```bash
# Deploy to sandbox environment
aws cloudformation create-stack \
  --stack-name component-vX-sandbox-test \
  --template-body file://cf-main-template.yaml \
  --parameters file://sandbox-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM

# Verify deployment success
aws cloudformation describe-stacks --stack-name component-vX-sandbox-test
```

#### 4.2 Test New Functionality
```bash
# Test new functionality
aws [service] describe-[resource] --name sandbox-test-app-[resource]

# Validate policies/configurations are applied
aws iam list-attached-role-policies --role-name sandbox-test-[component]-role

# Test backward compatibility with existing parameters
aws cloudformation create-stack \
  --stack-name component-vX-backward-test \
  --template-body file://cf-main-template.yaml \
  --parameters file://parameters-previous-version.json \
  --capabilities CAPABILITY_NAMED_IAM
```

---

### Step 5: Maintain Backward Compatibility

#### 5.1 Ensure Default Values for New Parameters
```yaml
# All new parameters must have safe defaults
NewFeatureEnabled:
  Type: String
  Default: "no"  # ✅ Safe default - doesn't change existing behavior
  
EnhancedLoggingEnabled:
  Type: String  
  Default: "false"  # ✅ Maintains current logging behavior
```

#### 5.2 Use Conditional Logic for New Features
```yaml
Conditions:
  EnableNewFeature: !Equals [!Ref NewFeatureEnabled, "yes"]
  
Resources:
  # Existing resources remain unchanged
  MainResource:
    Type: AWS::[Service]::[ResourceType]
    Properties:
      # ... existing properties ...
      
  # New resources only created when needed
  NewFeatureResource:
    Type: AWS::[Service]::[PolicyOrRole]
    Condition: EnableNewFeature
    Properties:
      # ... new feature resource definition ...
```

---

### Step 6: Version Tag Updates Across All Templates

#### 6.1 Update Version Tags in ALL Templates
**Even if a template has no functional changes, update version tags:**

```yaml
# In cf-main-template.yaml (main changes)
Tags:
  - Key: IaCVersion
    Value: InfraPlatform-[Component]-V[X]  # Updated from V[X-1]

Description: "[Component] Infrastructure Template - Version X.0"  # Updated

# In cf-additional-template.yaml (no functional changes but version update)
Tags:
  - Key: IaCVersion
    Value: InfraPlatform-[Component]-V[X]  # Updated from V[X-1]

Description: "[Component] Additional Template - Version X.0"  # Updated
```

---

### Step 7: Documentation Updates Using GitHub Copilot

#### 7.1 Update README.md with Copilot Assistance

**Copilot Prompt for README:**
```
Update the README.md for [Component] templates v[X].0. Add documentation for new parameters:
- NewFeatureEnabled (yes/no) - enables new feature functionality
- EnhancedLoggingEnabled (true/false) - enables enhanced logging and monitoring

Include usage examples and update the version comparison table.
```

**Example README Updates:**
```markdown
# [Component] Infrastructure Templates - Version X.0

## What's New in vX.0
- **New Feature**: Enhanced functionality for [specific use case]
- **Improved Configuration**: Multiple configuration levels available
- **Backward Compatibility**: All existing deployments continue to work
- **Better Performance**: Optimized resource allocation and management

## New Parameters in vX.0

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| NewFeatureEnabled | String | "no" | Enable new feature functionality |
| EnhancedLoggingEnabled | String | "false" | Enable enhanced logging and monitoring |

## Usage Examples

### Standard Deployment (Existing Behavior)
```bash
aws cloudformation create-stack \
  --stack-name my-component-stack \
  --template-body file://cf-main-template.yaml \
  --parameters file://parameters-standard.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### New Feature Deployment
```bash
aws cloudformation create-stack \
  --stack-name my-enhanced-component \
  --template-body file://cf-main-template.yaml \
  --parameters file://parameters-enhanced.json \
  --capabilities CAPABILITY_NAMED_IAM
```
```

#### 7.2 Update Release Notes with Copilot

**Copilot Prompt for Release Notes:**
```
Update release-notes.md for EKS v6.0 release. Document:
- New flexible deployment architecture features
- Two new parameters added for multi-project support
- Backward compatibility maintained
- Testing completed in sandbox
- Version tag updates across all templates
```

**Example Release Notes Update:**
```markdown
# Release Notes: EKS Infrastructure Templates

## Version 6.0 - November 10, 2025

### � Flexible Deployment Architecture
- **Multi-Project Support**: Deploy additional applications to existing EKS clusters
- **Infrastructure Reuse**: Share cluster resources while maintaining application isolation
- **Cost Optimization**: 50-60% infrastructure cost reduction for additional projects

### 🆕 New Parameters
- **SecondProjectForExistingEKS**: Boolean flag to enable flexible deployment
- **SourceProjectAppShortName**: Reference to original project for infrastructure reuse

### 🔄 Backward Compatibility
- ✅ All existing v5.0 deployments continue to work without changes
- ✅ New parameters have safe defaults
- ✅ No breaking changes introduced

### 🧪 Testing Completed
- ✅ Sandbox environment validation
- ✅ Backward compatibility testing
- ✅ Multi-project deployment verification
- ✅ CloudFormation template validation

### 📊 Template Updates
- **cf-main-template.yaml**: New feature implementation and parameters
- **cf-additional-template.yaml**: Version tags updated to V[X]
- **Other templates**: Version tags updated to V[X]

### 🏷️ Version Tags
All templates updated from `InfraPlatform-[Component]-V[X-1]` to `InfraPlatform-[Component]-V[X]`
```

---

### Step 8: Commit and Sync Changes

#### 8.1 Commit Changes Using VS Code GUI

**Step 1: Notice Change Indicators**
1. **Check Activity Bar** (left side) - you'll see the Source Control icon with a number badge (like "1" in your screenshot)
2. **The number indicates** how many files have been modified
3. **This confirms** VS Code has detected your changes

**Step 2: Open Source Control Panel**
1. **Click the Source Control icon** in the Activity Bar (with the number badge), or
2. **Press `Ctrl+Shift+G`** to open Source Control panel
3. **Review all changed files** in the Changes section

**Step 3: Stage Files for Commit**
1. **In the Changes section**, you'll see all modified files
2. **If you haven't staged files yet**, VS Code will show a dialog:
   ```
   "There are no staged changes to commit.
   Would you like to stage all your changes and commit them directly?"
   ```
3. **Click "Yes"** to stage all changes automatically, or
4. **Click "Always"** if you want VS Code to always stage changes automatically, or
5. **Click "Never"** if you prefer manual staging, or
6. **Click "Cancel"** to stage files manually first

**Manual Staging (Alternative):**
1. **Click the "+" icon** next to each file to stage individually
2. **Verify staged files** appear in "Staged Changes" section

**Step 4: Write Descriptive Commit Message**
In the commit message box (where it says "Message (Ctrl+Enter to co...")

**For Short Description:**
```
feat([component]): v[X].0 - Add [brief feature description]
```

**For Detailed Commit Message:**
```
feat([component]): v[X].0 - Add [feature description]

Features:
- Add NewFeatureEnabled parameter for [specific functionality]
- Add EnhancedLoggingEnabled parameter for [monitoring capabilities]
- Implement conditional logic with proper defaults
- Maintain full backward compatibility with v[X-1].0

Templates Updated:
- cf-main-template.yaml: New feature implementation and parameters
- cf-additional-template.yaml: Version tags updated to V[X]
- README.md: Documentation updated with v[X].0 features
- release-notes.md: Comprehensive v[X].0 changelog

Breaking Changes: None
Migration Required: None - optional new parameters with safe defaults
```

**Step 5: Commit and Sync Options**
1. **Click the dropdown arrow** next to the "Commit" button
2. **You'll see several options:**
   - **Commit**: Just commit locally
   - **Commit (Amend)**: Modify the last commit
   - **Commit & Push**: Commit and push to remote branch
   - **Commit & Sync**: Commit, pull latest changes, then push (recommended)

**Step 6: Choose "Commit & Sync" (Recommended)**
1. **Select "Commit & Sync"** from the dropdown
2. **VS Code will show a confirmation dialog:**
   ```
   "This action will pull and push commits from and to 'origin/eks-update'."
   ```
3. **Click "OK"** to proceed with the sync operation
4. **Optional: Check "OK, Don't Show Again"** if you don't want this confirmation in the future
5. **VS Code will automatically:**
   - Commit your changes locally
   - Pull any new changes from the remote branch
   - Push your changes to the remote repository
6. **Watch the status bar** for sync completion confirmation

**Step 7: Visual Confirmation**
1. **Source Control badge** will disappear from Activity Bar (no more number)
2. **Status bar** will show sync progress and completion
3. **Branch indicator** will update to show you're up to date
4. **Changes section** will be empty (all changes committed)
5. **You'll see your changes** reflected in the Azure DevOps web interface

**Step 8: Verify Changes in Azure DevOps Web Interface**
1. **Open your browser** and navigate to:
   ```
   https://dev.azure.com/IHIS-HIP/SEED%20InnerSource/_git/IaC-Templates
   ```
2. **Select your branch** from the branch dropdown (you'll see "eks-update" or your feature branch name)
3. **You'll see your changes listed**, including:
   - **Recent update notification**: "You updated [branch] Just now"
   - **File changes**: All modified files with timestamps
   - **Commit message**: Your commit description visible
4. **Verify the structure**, you should see:
   - Your version folder (e.g., `InfraPlatform/eks/v6/`)
   - All updated templates with current timestamps
   - Documentation files showing recent updates
5. **Confirm files are present**:
   - `cf-eks.yaml`
   - `cf-eks-fp.yaml`
   - `cf-eks-secrets.yaml`
   - `cf-nlb-tg-alb.yaml`
   - `README.md`
   - `SEED_INNERSOURCE_CLOUDFORMATION_UPDATE_PROCESS.md` (if updated)

**Visual Confirmation in Azure DevOps:**
- **Branch indicator**: Shows your current branch (e.g., "eks-update")
- **File timestamps**: Show "Just now" for recently committed files
- **Commit history**: Your commit appears in the recent changes
- **Create a pull request** button is available (for next step)

**Alternative: Quick Commit for Small Changes**
For minor updates or documentation changes:
1. **Write short message:** `docs: update EKS v6.0 documentation`
2. **Click "Commit & Sync"** directly
3. **VS Code handles everything automatically**

#### 8.2 Sync with Remote Repository Using VS Code

**Automatic Sync (When using "Commit & Sync")**
- **No additional steps needed** - VS Code automatically handles:
  - Fetching latest remote changes
  - Merging if needed
  - Pushing your commits
  - Resolving simple conflicts

**Manual Sync (Alternative Method)**

**Step 1: Fetch Latest Changes**
1. **Press `Ctrl+Shift+P`** (Command Palette)
2. **Type "Git: Fetch"** and select it
3. **Wait for fetch to complete**

**Step 2: Check for Conflicts**
1. **Check status bar** for any merge conflict indicators
2. **If conflicts exist:**
   - VS Code will show conflict markers in files
   - Resolve conflicts using VS Code's merge editor
   - Stage resolved files

**Step 3: Sync Changes**
1. **Click "Sync Changes" button** in Source Control panel (circular arrow icon)
2. **Or use Command Palette:** `Ctrl+Shift+P` → "Git: Sync"
3. **Confirm sync** when prompted

**Alternative: Manual Pull and Push**
1. **Pull latest changes:**
   - `Ctrl+Shift+P` → "Git: Pull"
2. **Push your changes:**
   - `Ctrl+Shift+P` → "Git: Push"

---

### Step 9: Create Pull Request to develop-iac Branch

#### 9.1 Create Pull Request via Azure DevOps Web Interface

**Step 1: Navigate to Pull Requests**
1. **In Azure DevOps**, go to **Repos → Pull requests**
2. **Click "New pull request"** button (top right)
3. **Or click "Create a pull request"** if you see the notification banner

**Step 2: Configure Pull Request Branches**
1. **Source branch**: Should show your feature branch (e.g., "eks-update")
2. **Target branch**: Select "Develop-IAC" from dropdown
3. **Verify the direction**: `eks-update` → `Develop-IAC`

**Step 3: Add Pull Request Title**
In the **Title** field (marked as required), enter:
```
[[Component]] v[X].0 - Add [Feature Description] for [Use Case]
```

**Step 4: Add Comprehensive Description**
In the **Description** field, paste the following template:

**PR Description Template for Azure DevOps:**
```markdown
## 🎯 Summary
Implement flexible deployment architecture for EKS templates v6.0, enabling multiple applications to deploy to the same EKS cluster while maintaining proper isolation and security.

## � Related Work Items
- **User Story:** #[WorkItemNumber] - Multi-project EKS deployment support
- **Task:** #[TaskNumber] - Update CloudFormation templates for flexible deployment
- **Bug:** #[BugNumber] - Fix CloudFormation Fn::Sub syntax issues (if applicable)

## �📋 Changes Made

### CloudFormation Templates
- ✅ **cf-eks-fp.yaml**: Added flexible deployment logic with conditional IAM policies
- ✅ **cf-eks-secrets.yaml**: Added dynamic KMS key resolution based on deployment mode
- ✅ **cf-eks.yaml**: Updated version tags to V6 (no functional changes)
- ✅ **cf-nlb-tg-alb.yaml**: Updated version tags to V6 (no functional changes)

### New Parameters Added
| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| SecondProjectForExistingEKS | String | "no" | Control deployment mode (primary/secondary) |
| SourceProjectAppShortName | String | "" | Reference original project for infrastructure reuse |

### Documentation Updates
- ✅ **README.md**: Updated to v6.0 with new parameter documentation
- ✅ **release-notes.md**: Comprehensive v6.0 changelog added
- ✅ **Usage Examples**: Added deployment examples for new features

## 🧪 Testing Completed

### Functional Testing
- ✅ **Primary Deployment**: New cluster creation works correctly
- ✅ **Secondary Deployment**: Existing cluster reuse functions properly
- ✅ **Backward Compatibility**: v5.0 parameter files work without modification
- ✅ **Conditional Logic**: UseSourceProject condition works as expected

## 🔄 Backward Compatibility
- ❌ **No Breaking Changes**: All existing v5.0 deployments continue to work
- ✅ **Safe Defaults**: New parameters default to existing behavior
- ✅ **Optional Features**: Flexible deployment is opt-in only

## 📁 Files Modified
```
InfraPlatform/eks/v6/
├── cf-eks-fp.yaml (Major: Flexible deployment implementation)
├── cf-eks-secrets.yaml (Major: Dynamic KMS resolution)
├── cf-eks.yaml (Minor: Version tags only)
├── cf-nlb-tg-alb.yaml (Minor: Version tags only)
├── parameters-eks-fp.json (Updated: New parameter examples)
├── parameters-eks-secrets.json (Updated: New parameter examples)
├── README.md (Major: v6.0 documentation)
└── release-notes.md (Major: v6.0 changelog)
```

## ✅ Definition of Done Checklist
- [ ] New features tested in development environment
- [ ] Documentation updated and reviewed
- [ ] Version tags updated consistently across all templates
- [ ] No breaking changes introduced
- [ ] Release notes are comprehensive and accurate
- [ ] Parameter naming follows established conventions
- [ ] Backward compatibility maintained and tested

## 👥 Required Reviewers
- [ ] **IAC Cloud Infrastructure Team**: @iac-cloud-infra-team
- [ ] **Checkin Team**: @checkin-team  
- [ ] **Security Review** (if applicable): @security-team
- [ ] **[Component] Component Owner**: @[component]-owner

## 🎯 Post-Merge Actions
- [ ] Update deployment automation pipelines
- [ ] Notify infrastructure teams of new capabilities
- [ ] Update internal wiki documentation
- [ ] Plan production rollout communication strategy

## 📝 Additional Notes
- This implementation follows SEED InnerSource governance standards
- Templates maintain consistency with existing naming conventions
- All changes are opt-in to ensure zero impact on existing deployments
```

#### 9.3 Azure DevOps Specific Configuration

**Work Item Linking:**
1. **In Pull Request description**, reference work items using `#[WorkItemNumber]`
2. **Add tags** relevant to your component: `eks`, `infrastructure`, `cloudformation`
3. **Set completion options (Optional - up to checkin owner to decide):**
   - ☐ Delete source branch after merging (optional)
   - ☐ Complete linked work items after merging (optional)
   - ☐ Squash changes when merging (optional)

**Branch Policies Configuration:**
- **Minimum reviewers**: 2 required approvals (IAC Cloud Infra + Checkin Team)
- **Required reviewers**: IAC Cloud Infrastructure team and Checkin team
- **Build validation**: CloudFormation template validation pipeline
- **Comment requirements**: Resolve all comments before merge

#### 9.4 Required Approvals in Azure DevOps
#### 9.4 Required Approvals and Review Process

**Must include these approvals:**
- **IAC Cloud Infrastructure Team** - CloudFormation templates, architecture and infrastructure design review
- **Checkin Team** - Process compliance, quality gates and governance review
- **Security Team** (if security changes) - Security policy review

**Review Process:**
1. **Automated Checks**: Azure DevOps will run validation pipelines
2. **Code Review**: Reviewers examine CloudFormation templates and documentation
3. **Approval Required**: All required reviewers must approve before merge
4. **Comments Resolution**: Address any feedback or questions from reviewers

**Step 9: Post-Creation Actions**
1. **Notify reviewers** via Azure DevOps notifications or direct communication
2. **Monitor for feedback** and respond promptly to comments
3. **Make updates** if requested by reviewers
4. **Track approval status** in the PR interface

**Step 10: Review Pull Request Content**
After creating the PR, you and reviewers can examine the changes:

**Overview Tab:**
- **Summary**: Shows total number of changed files (e.g., "16 changed files")
- **Branch direction**: Confirms `eks-update` → `Develop-IAC` 
- **Commits**: Lists all commits included in the PR (e.g., "7" commits)
- **High-level metrics**: Quick overview of scope and impact

**Files Tab - Detailed Change Review:**
1. **File Structure View**: Left panel shows all modified files organized by folder
   - `InfraPlatform/eks/v5/env/` - Parameter files
   - `InfraPlatform/eks/v6/env/` - New version parameter files
   - CloudFormation templates with change indicators

2. **Line-by-Line Diff View**: Right panel shows exact changes
   - **Green lines (+)**: New additions to files
   - **Red lines (-)**: Removed or modified content
   - **Line numbers**: Precise location of each change
   - **Parameter updates**: Shows old vs new parameter values

3. **Change Indicators**: 
   - **+46**: Files with additions (e.g., parameters-eks-fp.json)
   - **-3 +3**: Files with modifications (e.g., parameters-eks.json)
   - **File icons**: Different icons for .json, .yaml, .md files

**What Reviewers Can See:**
- **Exact parameter changes**: Old subnet IDs vs new ones
- **New file additions**: v6 folder structure and templates
- **Documentation updates**: README and release notes changes
- **Configuration changes**: Parameter value modifications
- **Template updates**: CloudFormation template improvements

**Benefits for Review Process:**
- **Transparency**: All changes visible in detail
- **Context**: Full file structure shows impact scope  
- **Precision**: Line-level changes enable thorough review
- **Comparison**: Easy to see what changed between versions

---

### Step 10: Production Release (Develop-IAC to Master)

#### 10.1 Create Production Release PR via Azure DevOps

**Step 1: Navigate to Pull Requests**
1. **In Azure DevOps**, go to **Repos → Pull requests**
2. **Click "New pull request"** button

**Step 2: Configure Production Release Branches**
1. **Source branch**: Select "Develop-IAC" from dropdown
2. **Target branch**: Select "master" from dropdown  
3. **Verify the direction**: `Develop-IAC` → `master`

**Step 3: Add Production Release Title**
In the **Title** field, enter:
```
RELEASE: EKS v6.0 Production Deployment - Flexible Deployment Architecture
```

**Step 4: Add Production Release Description**
```markdown
## 🚀 Production Release Summary
Promote EKS Infrastructure Templates v6.0 to production with flexible deployment architecture capabilities.

## 📊 Release Metrics
- **Component**: EKS Infrastructure Templates
- **Version**: 6.0
- **Templates Modified**: 4 (cf-eks-fp.yaml, cf-eks-secrets.yaml, cf-eks.yaml, cf-nlb-tg-alb.yaml)
- **New Parameters**: 2 (SecondProjectForExistingEKS, SourceProjectAppShortName)
- **New Features**: Multi-project deployment support, cost optimization
- **Breaking Changes**: None

## 🎯 Production Readiness Checklist
- ✅ **Code Review**: Completed and approved by IAC Cloud Infra and Checkin teams
- ✅ **Documentation**: Comprehensive README and release notes updated
- ✅ **Backward Compatibility**: All existing v5.0 deployments continue to work
- ✅ **Testing**: Functional testing completed for both deployment modes

## � Business Impact
- **Cost Optimization**: 50-60% infrastructure cost reduction for additional projects
- **Resource Efficiency**: Better utilization of existing EKS cluster capacity
- **Deployment Speed**: 40% faster deployment for secondary applications
- **Operational Simplicity**: Centralized cluster management with application isolation

## 🔧 Technical Features
- **Multi-Project Support**: Deploy additional applications to existing EKS clusters
- **Conditional Logic**: Smart resource creation based on deployment mode
- **Dynamic Parameter Resolution**: Intelligent SSM parameter routing
- **Auto-generated Resource Names**: Prevents naming conflicts between projects

## 📋 Production Deployment Plan
1. **Merge to Master**: Complete PR merge to master branch
2. **Tag Release**: Create v6.0 production release tag
3. **Documentation Update**: Update production deployment guides
4. **Team Notification**: Notify all infrastructure teams of new capabilities
5. **Gradual Rollout**: Enable teams to adopt new features incrementally

## 🔄 Rollback Strategy
- **Previous Version**: v5.0 templates remain available in version folders
- **Rollback Method**: Revert to v5.0 templates if issues arise
- **Time Estimate**: < 15 minutes to switch template versions
- **Risk Level**: Very Low (new features are opt-in, existing deployments unaffected)

## 👥 Production Approvers Required
- [ ] **IAC Cloud Infrastructure Team**: @iac-cloud-infra-team  
- [ ] **Checkin Team**: @checkin-team
- [ ] **Release Manager**: @release-manager
- [ ] **Infrastructure Manager**: @infra-manager

## 📅 Release Information
- **Release Date**: November 10, 2025
- **Maintenance Window**: Not required (backward compatible, opt-in features)
- **Rollout Strategy**: Gradual adoption via new parameter usage
- **Support Coverage**: Standard infrastructure support applies

## 📞 Support and Escalation
- **Primary Contact**: IAC Cloud Infrastructure Team
- **Secondary Contact**: Infrastructure On-call
- **Emergency Escalation**: Infrastructure Manager
- **Documentation**: Updated README and process guides available

## 📁 Production Files Summary
```
InfraPlatform/eks/v6/ (Production Ready)
├── cf-eks-fp.yaml (Major: Flexible deployment implementation)
├── cf-eks-secrets.yaml (Major: Dynamic KMS resolution)
├── cf-eks.yaml (Minor: Version tags updated to V6)
├── cf-nlb-tg-alb.yaml (Minor: Version tags updated to V6)
├── parameters-eks-fp.json (Updated: Production parameter examples)
├── parameters-eks-secrets.json (Updated: Production parameter examples)
├── README.md (Major: v6.0 comprehensive documentation)
├── release-notes.md (Major: v6.0 production changelog)
└── SEED_INNERSOURCE_CLOUDFORMATION_UPDATE_PROCESS.md (New: Process guide)
```
```

**Step 5: Add Production Reviewers**
1. **IAC Cloud Infrastructure Team**: Technical and architecture validation
2. **Checkin Team**: Process compliance and production readiness
3. **Release Manager**: Production release approval and coordination  
4. **Infrastructure Manager**: Executive approval for production changes

**Step 6: Set Production Completion Options**
- ✅ **Delete source branch after merging**: No (keep Develop-IAC branch)
- ✅ **Complete linked work items after merging**: Yes
- ✅ **Squash changes when merging**: Optional (based on team preference)

**Step 7: Create Production Pull Request**
1. **Review all production information** for accuracy
2. **Click "Create"** to submit the production release PR
3. **Note the production PR number** for tracking and communication

#### 10.2 Production Review Process

**Review Stages:**
1. **IAC Cloud Infrastructure Team Review**: Technical validation and architecture approval
2. **Checkin Team Review**: Process compliance and production readiness verification
3. **Release Manager Review**: Production release coordination and approval
4. **Infrastructure Manager Review**: Executive sign-off for production deployment

**What Production Reviewers Will See:**
- **Overview**: All changes from develop-iac ready for production
- **Files**: Complete v6.0 template set with all improvements
- **Commits**: Full development history and change progression
- **Testing Evidence**: Documentation of validation and testing completed

#### 10.3 Production Approval and Deployment

**Step 1: Monitor Review Progress**
1. **Track approvals** from all required reviewers
2. **Respond to feedback** promptly if any concerns raised
3. **Address any questions** about production readiness

**Step 2: Final Production Merge**
Once all approvals are received:
1. **Azure DevOps will enable merge** when all conditions met
2. **Complete the merge** via Azure DevOps interface
3. **Confirm successful merge** to master branch

**Step 3: Post-Merge Production Actions**
1. **Verify merge completion** in master branch
2. **Create production release tag** (v6.0)
3. **Update production documentation** links
4. **Notify all infrastructure teams** of production availability
5. **Update internal wikis** and knowledge bases
6. **Archive feature branch** (develop-iac remains active)

**Step 4: Production Rollout Communication**
1. **Send announcement** to infrastructure teams
2. **Provide usage guidance** and examples
3. **Share documentation links** (README, release notes, process guide)
4. **Offer training sessions** if needed for new features
5. **Monitor adoption** and provide support

---

## 📊 Process Summary Checklist

### Development Phase
- [ ] ✅ Feature branch created from master
- [ ] ✅ New version folder created (v[X])
- [ ] ✅ All templates copied (even unchanged ones)
- [ ] ✅ Changes implemented with proper naming conventions
- [ ] ✅ Sandbox testing completed successfully
- [ ] ✅ Backward compatibility maintained
- [ ] ✅ Version tags updated across all templates

### Documentation Phase  
- [ ] ✅ README.md updated with Copilot assistance
- [ ] ✅ Release notes updated with comprehensive changelog
- [ ] ✅ Usage examples provided
- [ ] ✅ Parameter documentation complete

### Review and Approval Phase
- [ ] ✅ Committed and synced to feature branch
- [ ] ✅ PR created to develop-iac with detailed description
- [ ] ✅ Infrastructure team approval obtained
- [ ] ✅ Team lead approval obtained
- [ ] ✅ Security review completed (if applicable)
- [ ] ✅ Merged to develop-iac

### Production Release Phase
- [ ] ✅ Production PR created from develop-iac to master
- [ ] ✅ Production approvals obtained
- [ ] ✅ Merged to master branch
- [ ] ✅ Release tagged (v6.0)
- [ ] ✅ Deployment automation updated
- [ ] ✅ Teams notified

---

## 🎯 Success Criteria

### Technical Success
- Sandbox deployment completes without errors
- New features work as documented
- No regression in existing functionality
- Backward compatibility maintained

### Process Success
- Proper branch workflow followed
- All required approvals obtained
- Documentation updated comprehensively
- Version tags updated consistently
- Release properly tagged and tracked

### Business Success
- New capabilities available for teams
- No disruption to existing deployments
- Clear migration path for new features
- Support documentation available
- Knowledge transfer completed

---

**Document Version**: 1.0  
**Created**: November 10, 2025  
**Owner**: SEED InnerSource Infrastructure Team  
**Next Review**: February 10, 2026