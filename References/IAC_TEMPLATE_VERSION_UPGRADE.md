# IAC Migration Notes

## 📋 Overview
This document contains migration notes and guidelines for Infrastructure as Code (IaC) template updates and transitions within the SEED InnerSource environment. This includes detailed procedures for version migrations, pipeline updates, and CloudFormation stack transitions.

---

## 🔄 Migration History

### Version Migration Records

#### **Example 1: Straight Version Migration (V3 to V4)**

#### **Migration Details:**
- **Source Version**: V3
- **Target Version**: V4
- **Migration Type**: Sequential version upgrade (V3 → V4)
- **Pipeline**: azure-pipelines-[component].yml
- **Template**: cf-iac-template.yml@Main

#### **Example 2: Skip Version Migration (V3 to V5)**

#### **Migration Details:**
- **Source Version**: V3
- **Target Version**: V5
- **Skip Version**: V4 (direct migration V3 → V5)
- **Pipeline**: azure-pipelines-[component].yml
- **Template**: cf-iac-template.yml@Main

---

## 📝 Migration Guidelines

### Pre-Migration Checklist
Before starting any version migration, ensure the following:

- [ ] ✅ **Review Target Version Documentation**: 
  - Check README.md in target version (e.g., V4 for straight migration, V6 for skip version) for new features and changes
  - Review release-notes.md to understand what was introduced in the new template
  - For skip version migrations: Review all intermediate versions (e.g., V4, V5 when migrating V3→V6) and their release notes to understand changes between each version
  - **Skip Version Advisory**: Consult with SEED InnerSource maintainers to confirm if skip-level migration is advisable, or if incremental one-version-at-a-time migration is recommended based on complexity of changes
  - Identify any new parameters that have been added
- [ ] ✅ **Parameter Analysis and Update**:
  - Compare current local parameter files with new template requirements
  - Copy any new parameters introduced in SEED InnerSource templates to local parameter files
  - Update parameter values accordingly using samples available in parameter JSON files
  - Note: CloudFormation templates come from SEED InnerSource, only local parameter files need updating
  - Azure DevOps version control allows reverting parameter files if needed
- [ ] ✅ **Template Compatibility Review**:
  - Review CloudFormation template changes between versions in SEED InnerSource
  - Understand impact of new parameters on existing resources
  - Validate that new parameters have appropriate default values
- [ ] ✅ **Environment Access**: Ensure access to Azure DevOps and AWS Management Console
- [ ] ✅ **Notification**: Inform stakeholders about planned migration
- [ ] ✅ **Rollback Plan**: Prepare rollback strategy to previous version if needed (Azure DevOps version control enables easy reversion)

### Migration Process

#### **Step 0: Documentation Review and Parameter Preparation**
1. **Review Target Version Documentation**:
   ```
   Example 1 - Straight Migration (V3 → V4):
   ├── InfraPlatform/[component]/v4/README.md
   │   └── Review new features, parameters, and usage examples
   ├── InfraPlatform/[component]/v4/release-notes.md  
   │   └── Understand what was introduced in V4
   └── InfraPlatform/[component]/v4/cf-*.yaml
       └── Identify new parameters and their descriptions

   Example 2 - Skip Version Migration (V3 → V5):
   ├── InfraPlatform/[component]/v4/README.md
   │   └── Review V4 changes (even though skipping)
   ├── InfraPlatform/[component]/v4/release-notes.md  
   │   └── Understand what was introduced in V4
   ├── InfraPlatform/[component]/v5/README.md
   │   └── Review V5 features and parameters
   ├── InfraPlatform/[component]/v5/release-notes.md  
   │   └── Understand what was introduced in V5
   └── InfraPlatform/[component]/v5/cf-*.yaml
       └── Identify all new parameters from V4 and V5
   ```

2. **Parameter Analysis and Migration**:
   - **Compare Parameter Files**:
     ```bash
     # Example 1 - Straight Migration (V3 → V4):
     Current: /eks/eks-cluster/env/prod-parameters.json
     SEED Template: InfraPlatform/eks/v4/parameters-*.json (for reference only)
     
     # Example 2 - Skip Version Migration (V3 → V5):
     Current: /eks/eks-cluster/env/prod-parameters.json
     SEED Template V4: InfraPlatform/eks/v4/parameters-*.json (review for intermediate changes)
     SEED Template V5: InfraPlatform/eks/v5/parameters-*.json (final target reference)
     ```
   
   - **Copy New Parameters**: 
     ```json
     // Example 1 - Straight Migration (V3 → V4):
     // Add only V4 new parameters
     {
       "ParameterKey": "EnableClusterLogging",
       "ParameterValue": "true"
     },
     {
       "ParameterKey": "LogRetentionDays",
       "ParameterValue": "30"
     }
     
     // Example 2 - Skip Version Migration (V3 → V5):
     // Add all parameters introduced in V4 and V5
     {
       "ParameterKey": "EnableClusterLogging",
       "ParameterValue": "true"
     },
     {
       "ParameterKey": "LogRetentionDays",
       "ParameterValue": "30"
     },
     {
       "ParameterKey": "EnableEnhancedMonitoring", 
       "ParameterValue": "false"
     },
     {
       "ParameterKey": "BackupRetentionPeriod",
       "ParameterValue": "7"
     },
     {
       "ParameterKey": "EnableEncryptionAtRest",
       "ParameterValue": "true"
     }
     ```

   - **Update Parameter Values**:
     - Use samples available in SEED InnerSource parameter JSON files as reference
     - Update values according to project-specific requirements
     - Refer to CloudFormation template for parameter descriptions and allowed values
     - Note: CloudFormation templates are sourced from SEED InnerSource, only local parameter files are modified

3. **Documentation Synchronization**:
   - **CloudFormation Templates**: Review parameter definitions in SEED InnerSource CF templates
   - **Local Documentation**: Update project README.md with new parameter usage examples
   - **Release Notes**: Document new parameters and their impact on deployments

#### **Step 1: Pipeline Configuration Update**
1. **Locate Pipeline**: Find the pipeline associated with the current version (V3)
   ```yaml
   # Example: azure-pipelines-[component].yml
   # Located in: Ccdp-Iac > [component] > [sub-component] > azure-pipelines-[component].yml
   ```

2. **Edit Pipeline Configuration**: 
   - Navigate to Azure DevOps repository structure:
     ```
     Ccdp-Iac/
     ├── activemq/
     ├── alb/
     ├── amp/
     ├── apigateway/
     ├── ec2/
     ├── eks/
     │   ├── eks-cluster/
     │   │   ├── env/
     │   │   │   ├── nprd-dev-parameters.json
     │   │   │   ├── nprd-sit-parameters.json
     │   │   │   ├── nprd-uat-parameters.json
     │   │   │   └── prod-parameters.json
     │   │   └── azure-pipelines-eks-cluster.yml ← Example target file
     │   ├── eks-fp/
     │   ├── eks-fp-ccdpnp/
     │   └── eks-nlb/
     ├── elasticache/
     ├── grafana/
     ├── rds/
     ├── s3/
     └── [other components]/
     ```
   
   - Update pipeline YAML configuration to reference V5 version:
     ```yaml
     # Pipeline Configuration Updates:
     variables:
       - group: HIP
       - name: PROJECT_NAME
         value: CCDP
       - name: RESOURCE_NAME  
         value: eks-cluster
     
     parameters:
       - name: 'Environments'
         type: object
         default:
           - EnvName: 'nprd-dev'
             StackName: '$(PROJECT_NAME)-nprd-dev-$(RESOURCE_NAME)'
             LocalParametersFileName: 'nprd-dev-parameters.json'
           - EnvName: 'nprd-sit'
             StackName: '$(PROJECT_NAME)-nprd-sit-$(RESOURCE_NAME)'
             LocalParametersFileName: 'nprd-sit-parameters.json'
           - EnvName: 'nprd-uat'
             StackName: '$(PROJECT_NAME)-nprd-uat-$(RESOURCE_NAME)'
             LocalParametersFileName: 'nprd-uat-parameters.json'
           - EnvName: 'PROD'
             StackName: '$(PROJECT_NAME)-prod-$(RESOURCE_NAME)'
             LocalParametersFileName: 'prod-parameters.json'
     
     extends:
       template: cf-iac-template.yml@Main
       parameters:
         Environments: '${{ parameters.Environments }}'
         MasterCFTemplateFilename: 'cf-[component].yaml'
         # Example 1 - Straight Migration (V3 → V4):
         MasterCFTemplateFolder: 'InfraPlatform/[component]/v4'  # Updated from v3 to v4
         # Example 2 - Skip Version Migration (V3 → V5):
         # MasterCFTemplateFolder: 'InfraPlatform/[component]/v5'  # Updated from v3 to v5
         LocalParametersFolder: '[component]/[sub-component]/env'
         ProjectName: '$(PROJECT_NAME)'
         ResourceName: '$(RESOURCE_NAME)'
         ProjectComponentName: '$(PROJECT_NAME)-$(RESOURCE_NAME)'
     ```

3. **Save Configuration**: Commit and save the updated pipeline configuration

#### **Step 2: Build Pipeline Execution**
1. **Trigger Build**: 
   - Navigate to **ccdp-aws-iac-[component]** pipeline in Azure DevOps
   - Manual build trigger, or automatic CI execution if enabled

2. **Monitor Build Process**:
   - Watch all pipeline stages in the **Runs** tab
   - Monitor build progression through stages
   - Recent successful builds show pattern like:
     ```
     #1.0.0.8 • Merged PR 94156: update eks v5 migration parameters
     #1.0.0.7 • Merged PR 94089: add new logging parameters (eks/eks-cluster)
     #1.0.0.6 • Merged PR 93987: update uat-parameters.json for v4 migration
     #1.0.0.5 • Merged PR 93368: update prod parameter.json (rds/rdssql)
     #1.0.0.4 • Merged PR 93367: Updated prod-parameters.json (rds/rdssql)
     #1.0.0.3 • Merged PR 92496: update prod parameter.json ([component]/[sub-component])
     #1.0.0.1 • Merged PR 74122: parameter-file-update
     ```
   - Ensure successful completion of:
     - Build validation ✅
     - Template compilation ✅
     - Parameter validation ✅
     - Artifact generation ✅

3. **Verify Build Success**: 
   - Confirm all stages show green checkmarks (✅)
   - Build status should show successful completion
   - All PR merges should be properly integrated

#### **Step 3: Release Pipeline Initiation**
1. **Access Build Summary**: Navigate to completed build summary page in Azure DevOps
2. **Initiate Release**: 
   - Click three dots (⋮) next to the successful build
   - Select "Release" to start release pipeline
3. **Navigate to Release Pipeline**:
   - Go to **IHIS-HIP** > **CCDP** > **Pipelines** > **Releases** > **ccdp-iac-[component]**
   - Monitor release progression: **Release-3** (or current release number)
4. **Execute "Create Change Set"**: 
   - Monitor pipeline stages:
     - **[UAT] Execute Change Set** ⭕ Not deployed
     - **[UAT] Delete Change Set** ⭕ Not deployed  
     - **[PROD] Create Change Set** ✅ Succeeded (on 6/4/2025, 3:24 PM)
     - **[PROD] Execute Change Set** ✅ Succeeded (on 6/4/2025, 3:30 PM)
   - Pipeline variables and history available in respective tabs

#### **Step 4: Change Set Review (AWS Console)**
1. **AWS Console Access**:
   - Log in to AWS Management Console
   - Navigate to **CloudFormation** > **Stacks**

2. **Locate Target Stack**:
   - Find the infrastructure stack associated with deployment
   - Example: `ccdp-iac-[component]` or similar naming convention
   - Stack should be in the region matching your deployment

3. **Review Change Set**:
   - Open stack and go to **Change Sets** tab
   - **⚠️ CRITICAL**: Carefully review all proposed changes before execution
   - Verify:
     - Resource modifications are expected
     - No unintended resource deletions
     - Parameter updates are correct:
       - **Example 1 (V3 → V4)**: Verify V4-specific parameter changes
       - **Example 2 (V3 → V5)**: Verify all V4 and V5 parameter changes combined
     - IAM policy changes are appropriate
     - Infrastructure component configurations align with target template specifications

4. **Change Set Validation Checklist**:
   - [ ] ✅ **Template Version**: Confirm change set reflects target template structure (V4 or V5)
   - [ ] ✅ **Resource Impact**: Review all resource modifications and additions
   - [ ] ✅ **Parameter Changes**: 
     - **Straight Migration**: Verify parameter updates match expected target version values
     - **Skip Migration**: Verify all intermediate and target version parameters are included
   - [ ] ✅ **IAM Changes**: Check any IAM role or policy modifications
   - [ ] ✅ **Network Changes**: Confirm VPC, subnet, and security group updates
   - [ ] ✅ **Component Specific**: Validate component-specific configurations and settings

#### **Step 5: Change Set Execution**
1. **Execute Change Set**:
   - Click "Execute" on the reviewed change set
   - Confirm execution when prompted

2. **Monitor Stack Update**:
   - Watch stack update progress in real-time
   - Check for failed resources
   - Monitor CloudFormation events
   - Validate successful completion

3. **Post-Execution Validation**:
   - Verify all resources updated successfully
   - Test application functionality
   - Confirm no degradation in performance

### Post-Migration Validation

#### **Infrastructure Validation**
- [ ] ✅ **Stack Status**: CloudFormation stack shows `UPDATE_COMPLETE`
- [ ] ✅ **Resource Health**: All infrastructure component resources healthy
- [ ] ✅ **Connectivity**: Application connectivity maintained
- [ ] ✅ **Performance**: No performance degradation observed
- [ ] ✅ **Logs**: Check CloudWatch logs for errors
- [ ] ✅ **Monitoring**: Verify monitoring and alerts functional

#### **Pipeline Validation**
- [ ] ✅ **Build Success**: Pipeline builds successfully with V5 templates
- [ ] ✅ **Release Process**: Release pipeline executes without errors
- [ ] ✅ **Parameter Files**: All parameter files compatible with V5
- [ ] ✅ **Version Tags**: IaC version tags updated correctly

---

## 🚨 Known Issues and Resolutions

### Common Migration Issues

#### **Issue 1: Missing New Parameters**
**Problem**: Migration fails because new required parameters are not included in project parameter files
**Resolution**:
- **Identify Missing Parameters**:
  ```bash
  # Example 1 - Straight Migration (V3 → V4):
  diff project/eks/eks-cluster/env/prod-parameters.json \
       seed-innersource/InfraPlatform/eks/v4/parameters-eks.json
  
  # Example 2 - Skip Version Migration (V3 → V5):
  # First check what changed in V4:
  diff seed-innersource/InfraPlatform/eks/v3/parameters-eks.json \
       seed-innersource/InfraPlatform/eks/v4/parameters-eks.json
  
  # Then check what changed in V5:
  diff seed-innersource/InfraPlatform/eks/v4/parameters-eks.json \
       seed-innersource/InfraPlatform/eks/v5/parameters-eks.json
  
  # Finally compare project with target:
  diff project/eks/eks-cluster/env/prod-parameters.json \
       seed-innersource/InfraPlatform/eks/v5/parameters-eks.json
  ```
- **Add Required Parameters**: Copy new parameters with appropriate values
- **Validate Parameter Values**: Use SEED InnerSource samples as reference and refer to CloudFormation templates for validation rules
- **Update Documentation**: Ensure all new parameters are documented in project README.md

#### **Issue 2: Change Set Review Failures**
**Problem**: Change set contains unexpected resource deletions
**Resolution**: 
- **STOP EXECUTION** immediately
- Review template differences between source and target versions
- **Straight Migration**: Compare V3 and V4 templates
- **Skip Migration**: Compare V3 with intermediate (V4) and final (V5) versions
- Consult with infrastructure team before proceeding
- **For Skip Migrations**: Consider incremental approach (V3 → V4 → V5) if changes are too complex

#### **Issue 3: IAM Permission Changes**
**Problem**: New templates require additional IAM permissions
**Resolution**: 
- Review IAM policy updates in change set
- **Straight Migration**: Check V4-specific IAM changes
- **Skip Migration**: Review cumulative IAM changes from V4 and V5
- Ensure service accounts have necessary permissions
- Update IAM roles as required before execution

### Rollback Procedures

#### **Emergency Rollback**
If migration fails and immediate rollback is required:

1. **Revert Pipeline Configuration**:
   ```yaml
   # Restore V3 configuration
   template: cf-iac-template.yml@Main
   MasterCFTemplateFolder: 'InfraPlatform/[component]/v3'
   ```

2. **Execute Rollback Build**: Trigger new build with V3 configuration
3. **Create Rollback Change Set**: Follow same change set process
4. **Execute with Caution**: Review rollback changes carefully

---

## 📚 References and Resources

### Documentation Links
- **SEED InnerSource CloudFormation Update Process**: `SEED_INNERSOURCE_CLOUDFORMATION_UPDATE_PROCESS.md`
- **Azure DevOps Pipeline Documentation**: Internal SEED documentation
- **AWS CloudFormation Best Practices**: AWS official documentation
- **EKS Template Documentation**: Component-specific README files

### Template Locations
```
Example 1 - Straight Migration (V3 → V4):
InfraPlatform/[component]/
├── v3/ (Source - being migrated from)
└── v4/ (Target - migrating to)

Example 2 - Skip Version Migration (V3 → V5):
InfraPlatform/[component]/
├── v3/ (Source - being migrated from)
├── v4/ (Intermediate - review for changes but skip deployment)
└── v5/ (Target - migrating to)
```

### Pipeline Locations
```
Azure DevOps Repository Structure:
Ccdp-Iac/
├── activemq/
├── alb/
├── amp/
├── apigateway/
├── ec2/
├── eks/
│   ├── eks-cluster/
│   │   ├── env/ (Environment parameter files)
│   │   │   ├── nprd-dev-parameters.json
│   │   │   ├── nprd-sit-parameters.json
│   │   │   ├── nprd-uat-parameters.json
│   │   │   └── prod-parameters.json
│   │   └── azure-pipelines-eks-cluster.yml (Main pipeline)
│   ├── eks-fp/
│   ├── eks-fp-ccdpnp/
│   └── eks-nlb/
├── elasticache/
├── grafana/
├── rds/
├── s3/
└── [other components]/

Pipeline Path: 
/[component]/[sub-component]/azure-pipelines-[component].yml

Release Pipeline:
Azure DevOps > IHIS-HIP > CCDP > Pipelines > Releases > ccdp-iac-[component]
```

### Contact Information
- **Migration Lead**: Mani Dineshkumar (Synapxe)
- **IAC Cloud Infrastructure Team**: @iac-cloud-infra-team
- **SEED InnerSource Support**: Internal support channels
- **Emergency Contact**: Infrastructure On-call

### Key Personnel
- **Lead Engineer**: Dineshkumar Mani
- **Contact**: +65 94230525
- **Organization**: Synapxe (UEN 200814464H)
- **Location**: 1 North Buona Vista Link, #05-01 Elementum, Singapore 139691

---

## 📊 Migration Success Metrics

### Technical Success Indicators
- ✅ **Pipeline Execution**: Build and release pipelines complete successfully
- ✅ **Stack Status**: CloudFormation stack reaches `UPDATE_COMPLETE` status
- ✅ **Resource Health**: All infrastructure resources operational
- ✅ **Zero Downtime**: No service interruption during migration
- ✅ **Performance Baseline**: Performance metrics maintained or improved

### Process Success Indicators
- ✅ **Documentation**: Migration steps documented and followed
- ✅ **Approval Process**: Proper change management followed
- ✅ **Communication**: Stakeholders informed throughout process
- ✅ **Validation**: Post-migration testing completed successfully

---

## 🎯 Best Practices for Future Migrations

### Planning Phase
1. **Version Strategy**: Consider incremental migrations for major version jumps
2. **Documentation Review**: Thoroughly review target version README and release notes
3. **Parameter Analysis**: Compare SEED InnerSource templates with project parameter files
4. **Testing**: Always test in lower environments first
5. **Timing**: Schedule during maintenance windows when possible
6. **Communication**: Notify all affected teams in advance

### Execution Phase
1. **Documentation Synchronization**: Ensure all new parameters are properly documented
2. **Parameter Migration**: Copy and update new parameters from SEED InnerSource templates
3. **Change Set Review**: Never skip careful change set review
4. **Monitoring**: Monitor all stages of migration process
5. **Backup**: Ensure rollback procedures are ready
6. **Documentation**: Document any deviations or issues encountered

### Post-Migration
1. **Validation**: Comprehensive testing of all functionality
2. **Monitoring**: Enhanced monitoring for 24-48 hours post-migration
3. **Documentation**: Update all relevant documentation
4. **Lessons Learned**: Capture insights for future migrations

---

**Document Version**: 1.1  
**Created**: November 11, 2025  
**Based on Migration**: V3 to V5 EKS Templates (October 2, 2025)  
**Owner**: SEED InnerSource Infrastructure Team  
**Next Review**: February 11, 2026