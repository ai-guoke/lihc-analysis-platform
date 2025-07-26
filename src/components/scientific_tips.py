"""
科学原理提示组件
为每个分析模块提供科学基础知识和设计理念的说明
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash

def create_scientific_tip(module_name, tip_id):
    """
    创建科学原理提示按钮和卡片式弹出框
    
    Args:
        module_name: 模块名称
        tip_id: 提示框的唯一ID
    
    Returns:
        包含按钮和卡片弹出框的组件
    """
    # 提示按钮
    tip_button = html.Button(
        [
            html.I(className="fas fa-lightbulb me-1"),
            html.Span("科学原理", className="d-none d-sm-inline")
        ],
        id=f"open-{tip_id}",
        className="scientific-tip-button",
        style={
            "backgroundColor": "#17a2b8",
            "color": "white",
            "border": "none",
            "borderRadius": "20px",
            "padding": "6px 16px",
            "fontSize": "0.85rem",
            "cursor": "pointer",
            "transition": "all 0.3s ease",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
    )
    
    # 获取该模块的科学原理内容
    content = get_scientific_content(module_name)
    
    # 卡片式弹出框
    card_popup = html.Div(
        [
            # 背景遮罩
            html.Div(
                id=f"backdrop-{tip_id}",
                className="scientific-tip-backdrop",
                style={
                    "position": "fixed",
                    "top": 0,
                    "left": 0,
                    "width": "100%",
                    "height": "100%",
                    "backgroundColor": "rgba(0, 0, 0, 0.5)",
                    "zIndex": 1040,
                    "display": "none",
                    "backdropFilter": "blur(2px)"
                }
            ),
            # 卡片内容
            html.Div(
                [
                    # 卡片头部
                    html.Div(
                        [
                            html.H4(
                                [
                                    html.I(className="fas fa-lightbulb me-2", style={"color": "#ffc107"}),
                                    f"{module_name} - 科学原理"
                                ],
                                className="mb-0",
                                style={"color": "#2c3e50"}
                            ),
                            html.Button(
                                "×",
                                id=f"close-{tip_id}",
                                className="scientific-tip-close",
                                style={
                                    "position": "absolute",
                                    "top": "15px",
                                    "right": "15px",
                                    "background": "none",
                                    "border": "none",
                                    "fontSize": "1.5rem",
                                    "cursor": "pointer",
                                    "color": "#6c757d",
                                    "lineHeight": 1,
                                    "padding": "0 5px"
                                }
                            )
                        ],
                        className="scientific-card-header",
                        style={
                            "padding": "20px 25px",
                            "borderBottom": "1px solid #e9ecef",
                            "backgroundColor": "#f8f9fa",
                            "borderRadius": "12px 12px 0 0",
                            "position": "relative"
                        }
                    ),
                    # 卡片主体
                    html.Div(
                        [
                            # 选项卡导航
                            dbc.Tabs(
                                [
                                    dbc.Tab(
                                        label="🔬 科学基础",
                                        tab_id="scientific-basis",
                                        label_style={"color": "#007bff"}
                                    ),
                                    dbc.Tab(
                                        label="💡 设计理念",
                                        tab_id="design-philosophy",
                                        label_style={"color": "#17a2b8"}
                                    ),
                                    dbc.Tab(
                                        label="📊 数学原理",
                                        tab_id="mathematical-principle",
                                        label_style={"color": "#28a745"}
                                    ),
                                    dbc.Tab(
                                        label="📚 参考文献",
                                        tab_id="references",
                                        label_style={"color": "#ffc107"}
                                    ),
                                ],
                                id=f"tabs-{tip_id}",
                                active_tab="scientific-basis",
                                className="mb-3"
                            ),
                            # 选项卡内容
                            html.Div(id=f"tab-content-{tip_id}", className="scientific-tab-content")
                        ],
                        className="scientific-card-body",
                        style={
                            "padding": "25px",
                            "maxHeight": "60vh",
                            "overflowY": "auto",
                            "overflowX": "hidden"
                        }
                    )
                ],
                id=f"card-{tip_id}",
                className="scientific-tip-card",
                style={
                    "position": "fixed",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0 10px 40px rgba(0, 0, 0, 0.2)",
                    "width": "90%",
                    "maxWidth": "800px",
                    "zIndex": 1050,
                    "display": "none",
                    "animation": "slideIn 0.3s ease-out"
                }
            )
        ],
        style={"position": "relative", "display": "inline-block"}
    )
    
    # 存储内容数据
    content_store = dcc.Store(
        id=f"content-store-{tip_id}",
        data=content
    )
    
    return html.Div([tip_button, card_popup, content_store], style={"display": "inline-block"})

def get_scientific_content(module_name):
    """
    获取各模块的科学原理内容
    """
    content_map = {
        "多维度分析": {
            "scientific_basis": """
            肿瘤微环境（Tumor Microenvironment, TME）是一个复杂的生态系统，包含肿瘤细胞、免疫细胞、
            基质细胞、细胞外基质和各种信号分子。传统的单一维度分析无法全面捕捉这种复杂性。
            我们基于系统生物学理论，将TME分解为五个关键维度，每个维度代表了肿瘤发生发展的不同方面。
            """,
            "design_philosophy": """
            我们的设计理念是"分而治之，合而用之"。首先将复杂的TME分解为可管理的维度，
            分别进行深入分析，然后通过整合算法将各维度信息融合，形成对肿瘤生物学特征的全面认识。
            这种方法既保证了分析的深度，又确保了结果的系统性。
            """,
            "mathematical_principle": """
            **维度评分计算**：
            ```
            Dimension_Score = Σ(wi × gi × ei) / Σ(wi)
            
            其中：
            - wi: 基因i在该维度的权重（基于文献挖掘）
            - gi: 基因i的表达水平（标准化后）
            - ei: 基因i的富集得分（GSEA）
            ```
            
            **综合评分**：
            ```
            Composite_Score = Π(Di^αi)
            
            其中：
            - Di: 第i个维度的得分
            - αi: 维度权重（通过机器学习优化）
            ```
            """,
            "references": [
                "Hanahan D, Weinberg RA. Hallmarks of cancer: the next generation. Cell. 2011",
                "Junttila MR, de Sauvage FJ. Influence of tumour micro-environment heterogeneity on therapeutic response. Nature. 2013",
                "Binnewies M, et al. Understanding the tumor immune microenvironment (TIME) for effective therapy. Nat Med. 2018"
            ]
        },
        
        "网络分析": {
            "scientific_basis": """
            基因和蛋白质不是孤立发挥作用的，而是通过复杂的相互作用网络协同工作。
            网络生物学认为，疾病往往是由于网络中关键节点或模块的功能失调导致的。
            通过构建和分析分子相互作用网络，我们可以识别在疾病发生发展中起关键作用的枢纽基因。
            """,
            "design_philosophy": """
            我们采用多层网络整合策略：1）基因共表达网络捕捉功能相关性；
            2）蛋白质相互作用网络反映物理相互作用；3）调控网络展示因果关系。
            通过整合这些不同层次的网络信息，我们能够更准确地识别真正的关键节点。
            """,
            "mathematical_principle": """
            **网络构建**：
            ```
            相关性阈值：|r| > 0.6 且 FDR < 0.05
            边权重：w(i,j) = |r(i,j)| × confidence_score
            ```
            
            **中心性度量**：
            ```
            1. 度中心性：DC(i) = ki / (n-1)
            2. 介数中心性：BC(i) = Σ(σst(i)/σst)
            3. 特征向量中心性：EC(i) = (1/λ) × Σ(aij × EC(j))
            ```
            
            **模块识别**（Louvain算法）：
            ```
            Q = (1/2m) × Σ[Aij - kikj/2m] × δ(ci, cj)
            ```
            """,
            "references": [
                "Barabási AL, Oltvai ZN. Network biology: understanding the cell's functional organization. Nat Rev Genet. 2004",
                "Vidal M, Cusick ME, Barabási AL. Interactome networks and human disease. Cell. 2011",
                "Langfelder P, Horvath S. WGCNA: an R package for weighted correlation network analysis. BMC Bioinformatics. 2008"
            ]
        },
        
        "Linchpin靶点": {
            "scientific_basis": """
            Linchpin（关键枢纽）概念源于系统生物学中的"关键节点"理论。在生物网络中，
            某些节点的改变会对整个系统产生级联效应。这些节点往往是理想的治疗靶点，
            因为靶向它们可以产生最大的治疗效果。
            """,
            "design_philosophy": """
            我们的Linchpin算法整合了四个关键维度：预后相关性（临床价值）、网络中心性（系统重要性）、
            跨维度连接性（调控广度）和调控重要性（功能影响）。这种多维度整合确保识别的靶点
            既有科学依据，又有临床转化潜力。
            """,
            "mathematical_principle": """
            **Linchpin评分算法**：
            ```
            Linchpin_Score = Σ(wi × norm(Si))
            
            评分组成：
            S1 = -log10(p_value) × sign(HR) × |log2(HR)|  # 预后评分
            S2 = 0.4×DC + 0.4×BC + 0.2×EC                  # 网络中心性
            S3 = Σ(cross_dim_edges) / total_edges          # 跨维度连接
            S4 = TF_targets + miRNA_targets                 # 调控重要性
            
            权重：w = [0.4, 0.3, 0.2, 0.1]（通过交叉验证优化）
            ```
            """,
            "references": [
                "Hwang S, et al. A protein interaction network associated with asthma. J Theor Biol. 2008",
                "Yildirim MA, et al. Drug-target network. Nat Biotechnol. 2007",
                "Hopkins AL. Network pharmacology: the next paradigm in drug discovery. Nat Chem Biol. 2008"
            ]
        },
        
        "生存分析": {
            "scientific_basis": """
            生存分析是评估预后因素的金标准方法。它考虑了事件发生的时间和删失数据，
            能够准确估计生存概率和风险比。在精准医学中，基于分子标志物的生存分析
            是实现患者分层和个体化治疗的关键。
            """,
            "design_philosophy": """
            我们采用多层次生存分析策略：1）单因素分析筛选候选基因；2）LASSO-Cox进行特征选择；
            3）多因素Cox模型构建风险评分；4）时间依赖性ROC验证模型性能。
            这种严格的统计流程确保了预后模型的稳健性和可重现性。
            """,
            "mathematical_principle": """
            **Cox比例风险模型**：
            ```
            h(t|x) = h0(t) × exp(β1x1 + β2x2 + ... + βpxp)
            
            风险比：HR = exp(β)
            ```
            
            **LASSO-Cox**：
            ```
            L(β) = -l(β) + λΣ|βj|
            
            其中：l(β)是Cox部分似然函数
            ```
            
            **风险评分**：
            ```
            Risk_Score = Σ(βi × Expressioni)
            
            分组：中位数或最佳截断值（maximally selected rank statistics）
            ```
            """,
            "references": [
                "Cox DR. Regression models and life-tables. J R Stat Soc Series B. 1972",
                "Simon N, et al. Regularization paths for Cox's proportional hazards model. J Stat Softw. 2011",
                "Heagerty PJ, Zheng Y. Survival model predictive accuracy and ROC curves. Biometrics. 2005"
            ]
        },
        
        "多组学整合": {
            "scientific_basis": """
            单一组学数据只能提供生物系统的局部视图。多组学整合通过同时分析基因组、
            转录组、蛋白质组和表观遗传组等多层次信息，能够揭示疾病的系统性特征
            和层次间的调控关系。
            """,
            "design_philosophy": """
            我们提供三种整合策略以适应不同的研究目的：1）早期整合（特征拼接）适合探索性分析；
            2）中期整合（SNF）适合发现患者亚型；3）晚期整合（MOFA）适合理解多组学间的关系。
            用户可根据具体需求选择合适的方法。
            """,
            "mathematical_principle": """
            **相似性网络融合（SNF）**：
            ```
            P(v+1) = S × W(v) × S^T
            W = Σ P(k) / K
            
            收敛后的W矩阵用于聚类分析
            ```
            
            **多组学因子分析（MOFA）**：
            ```
            Y(m) = W(m) × Z + ε(m)
            
            其中：
            - Y(m): 第m种组学数据
            - W(m): 载荷矩阵
            - Z: 潜在因子
            ```
            """,
            "references": [
                "Wang B, et al. Similarity network fusion for aggregating data types on a genomic scale. Nat Methods. 2014",
                "Argelaguet R, et al. Multi-Omics Factor Analysis—a framework for unsupervised integration of multi-omics data sets. Mol Syst Biol. 2018",
                "Subramanian I, et al. Multi-omics data integration, interpretation, and its application. Bioinform Biol Insights. 2020"
            ]
        },
        
        "ClosedLoop分析": {
            "scientific_basis": """
            因果推理是理解疾病机制的核心。ClosedLoop方法借鉴了流行病学中的Bradford Hill准则，
            通过整合多种独立证据类型来推断因果关系。只有当多条证据链都指向同一个基因时，
            我们才认为它是真正的因果驱动因素。
            """,
            "design_philosophy": """
            我们设计了一个"闭环"验证系统：从差异表达出发，经过生存关联、基因组改变、
            表观遗传调控，最终回到功能验证。每个环节都是独立的证据来源，
            多重证据的汇聚大大提高了因果推断的可信度。
            """,
            "mathematical_principle": """
            **证据整合模型**：
            ```
            Causal_Score = Σ(Evidence_i × Weight_i × Confidence_i)
            
            证据评分：
            E1 = |log2FC| × (-log10(FDR))           # 差异表达
            E2 = |log2(HR)| × (-log10(p_value))     # 生存关联
            E3 = CNV_frequency × expression_corr      # CNV驱动
            E4 = methylation_diff × expression_corr  # 甲基化调控
            E5 = mutation_frequency × driver_score    # 突变证据
            
            贝叶斯更新：
            P(Causal|Evidence) = P(Evidence|Causal) × P(Causal) / P(Evidence)
            ```
            """,
            "references": [
                "Hill AB. The environment and disease: association or causation? Proc R Soc Med. 1965",
                "Pearl J. Causality: Models, Reasoning and Inference. Cambridge University Press. 2009",
                "Schadt EE. Molecular networks as sensors and drivers of common human diseases. Nature. 2009"
            ]
        },
        
        "免疫微环境": {
            "scientific_basis": """
            肿瘤免疫微环境是决定免疫治疗效果的关键因素。通过分析免疫细胞浸润模式、
            免疫检查点表达和免疫相关基因特征，我们可以预测患者对免疫治疗的响应，
            并设计个性化的免疫治疗策略。
            """,
            "design_philosophy": """
            我们整合了多种去卷积算法（CIBERSORT、EPIC、quanTIseq）来准确估计免疫细胞组成，
            并结合免疫检查点表达、新抗原负荷等多维度信息，提供全面的免疫状态评估。
            这种综合方法能够识别"热肿瘤"和"冷肿瘤"，指导免疫治疗决策。
            """,
            "mathematical_principle": """
            **CIBERSORT去卷积算法**：
            ```
            minimize ||X - B × F||²₂ + λ||F||₁
            subject to: F ≥ 0, Σf = 1
            
            其中：
            - X: 混合表达矩阵
            - B: 细胞类型特征矩阵
            - F: 细胞比例矩阵
            ```
            
            **免疫评分**：
            ```
            Immune_Score = Σ(CTLs × w1) + Σ(Tregs × w2) + Σ(MDSCs × w3)
            
            免疫亚型分类：
            - Type I: TIL⁺ PD-L1⁺ (热肿瘤)
            - Type II: TIL⁻ PD-L1⁻ (冷肿瘤)
            - Type III: TIL⁺ PD-L1⁻ (免疫排斥)
            - Type IV: TIL⁻ PD-L1⁺ (固有耐药)
            ```
            """,
            "references": [
                "Newman AM, et al. Robust enumeration of cell subsets from tissue expression profiles. Nat Methods. 2015",
                "Thorsson V, et al. The immune landscape of cancer. Immunity. 2018",
                "Jiang P, et al. Signatures of T cell dysfunction and exclusion predict cancer immunotherapy response. Nat Med. 2018"
            ]
        },
        
        "药物响应预测": {
            "scientific_basis": """
            药物响应的个体差异主要源于肿瘤的分子异质性。通过整合基因表达、突变状态、
            拷贝数变异等多维度信息，结合大规模药物筛选数据库（如GDSC、CTRP），
            我们可以预测患者对不同药物的敏感性。
            """,
            "design_philosophy": """
            我们采用"双向验证"策略：1）从分子特征预测药物敏感性（正向）；
            2）从药物靶点反推分子特征（反向）。只有双向验证一致的预测结果
            才被认为是高可信度的。这种设计大大提高了预测的准确性。
            """,
            "mathematical_principle": """
            **弹性网络回归模型**：
            ```
            IC50 = β₀ + Σ(βᵢ × Geneᵢ) + Σ(γⱼ × Mutationⱼ) + ε
            
            损失函数：
            L = MSE + α[ρ||β||₁ + (1-ρ)||β||₂²/2]
            ```
            
            **深度学习模型（DrugCell）**：
            ```
            隐藏层：h = ReLU(W × x + b)
            注意力机制：a = softmax(Wₐ × h)
            输出：y = σ(Wₒ × (a ⊙ h))
            ```
            
            **药物组合协同效应**：
            ```
            Bliss Independence: Eₐᵦ = Eₐ + Eᵦ - Eₐ × Eᵦ
            协同指数：CI = (D₁/Dx₁) + (D₂/Dx₂)
            ```
            """,
            "references": [
                "Barretina J, et al. The Cancer Cell Line Encyclopedia enables predictive modelling of anticancer drug sensitivity. Nature. 2012",
                "Iorio F, et al. A landscape of pharmacogenomic interactions in cancer. Cell. 2016",
                "Kuenzi BM, et al. Predicting drug response and synergy using a deep learning model of human cancer cells. Cancer Cell. 2020"
            ]
        },
        
        "代谢分析": {
            "scientific_basis": """
            肿瘤细胞的代谢重编程是肿瘤的重要特征之一。与正常细胞不同，肿瘤细胞
            重新编程其代谢网络以满足快速增殖的需求。这种代谢改变不仅为肿瘤生长
            提供能量和物质基础，还影响肿瘤微环境和免疫逃逸。
            """,
            "design_philosophy": """
            我们的代谢分析模块整合了三个关键维度：1）代谢通路活性评估；
            2）代谢依赖性识别；3）代谢-免疫串扰分析。通过综合这些信息，
            我们能够识别肿瘤特异性的代谢脆弱点，为代谢靶向治疗提供指导。
            """,
            "mathematical_principle": """
            **代谢通路活性评分（ssGSEA）**：
            ```
            ES(P) = Σ(|r_j|^p / N_R) - Σ(1 / (N - N_hit))
            
            其中：
            - r_j: 基因j的表达排秩
            - p: 权重参数（通常为1）
            - N_R: 通路中基因总数
            ```
            
            **代谢依赖性评分**：
            ```
            Dependency_Score = -log10(p) × sign(ΔActivity) × |ΔSurvival|
            
            其中：
            - p: CRISPR筛选FDR
            - ΔActivity: 通路活性变化
            - ΔSurvival: 生存影响
            ```
            
            **代谢-免疫串扰分析**：
            ```
            Crosstalk_Score = cor(Metabolite_i, Immune_j) × w_i × w_j
            
            网络模块化：Q = Σ[δ(c_i, c_j) × (A_ij - k_i × k_j / 2m)]
            ```
            """,
            "references": [
                "Hanahan D, Weinberg RA. Hallmarks of cancer: the next generation. Cell. 2011",
                "Pavlova NN, Thompson CB. The Emerging Hallmarks of Cancer Metabolism. Cell Metab. 2016",
                "Li X, et al. Navigating metabolic pathways to enhance antitumour immunity and immunotherapy. Nat Rev Clin Oncol. 2019"
            ]
        },
        
        "异质性分析": {
            "scientific_basis": """
            肿瘤内异质性（ITH）是肿瘤进化和耐药的根源。肿瘤在发展过程中，
            不同克隆的出现和竞争导致复杂的克隆结构。理解肿瘤的克隆进化、
            空间分布和时间动态对于预测治疗响应和设计个体化治疗策略至关重要。
            """,
            "design_philosophy": """
            我们的异质性分析框架融合了多个维度：1）克隆结构推断；2）进化轨迹重建；
            3）空间异质性评估；4）时间动态监测。通过整合这些分析，
            我们能够全面理解肿瘤的复杂性，预测耐药风险，并设计组合治疗策略。
            """,
            "mathematical_principle": """
            **克隆结构推断（PyClone）**：
            ```
            P(C|φ) ∝ P(φ|C) × P(C)
            
            其中：
            - C: 克隆簇
            - φ: 等位基因频率（VAF）
            - 使用Dirichlet过程聚类
            ```
            
            **进化轨迹重建**：
            ```
            最大简约树：L = Σ w_ij × d_ij
            
            进化速率：dN/dS = (N_n/N_s) / (S_n/S_s)
            - N_n/N_s: 非同义/同义突变数
            - S_n/S_s: 非同义/同义位点数
            ```
            
            **空间异质性指数**：
            ```
            ITH_index = 1 - Σ(p_i^2)
            
            Morans I = (n/W) × ΣΣw_ij(x_i-μ)(x_j-μ) / Σ(x_i-μ)^2
            ```
            """,
            "references": [
                "McGranahan N, Swanton C. Clonal Heterogeneity and Tumor Evolution. Cell. 2017",
                "Dentro SC, et al. Characterizing genetic intra-tumor heterogeneity across 2,658 human cancer genomes. Cell. 2021",
                "Turajlic S, et al. Resolving genetic heterogeneity in cancer. Nat Rev Genet. 2019"
            ]
        },
        
        "分子分型": {
            "scientific_basis": """
            肿瘤的分子异质性是精准医疗的基础。通过无监督聚类方法识别具有相似分子特征的
            患者亚组，可以实现更精确的预后评估和治疗选择。分子分型已经在多种癌症中
            显示出重要的临床价值。
            """,
            "design_philosophy": """
            我们采用共识聚类（Consensus Clustering）确保分型的稳定性，并通过轮廓系数、
            CPI、Gap统计量等多个指标确定最优聚类数。每个亚型都经过生物学功能富集分析
            和临床特征关联验证，确保分型既有生物学意义又有临床价值。
            """,
            "mathematical_principle": """
            **共识聚类算法**：
            ```
            1. 重采样：对样本进行B次bootstrap
            2. 聚类：每次使用k-means/层次聚类
            3. 共识矩阵：M(i,j) = Σ(I(i,j same cluster)) / Σ(I(i,j both sampled))
            4. 最终聚类：对共识矩阵进行层次聚类
            ```
            
            **最优聚类数确定**：
            ```
            轮廓系数：s(i) = (b(i) - a(i)) / max(a(i), b(i))
            CPI：Consensus CDF曲线下面积变化率
            PAC：Proportion of Ambiguous Clustering
            ```
            
            **亚型特征提取**：
            ```
            SAM分析：找出亚型特异性基因
            GSVA：计算每个亚型的通路活性
            ```
            """,
            "references": [
                "Monti S, et al. Consensus clustering: a resampling-based method for class discovery. Machine Learning. 2003",
                "Verhaak RG, et al. Integrated genomic analysis identifies clinically relevant subtypes of glioblastoma. Cancer Cell. 2010",
                "Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. Nature. 2012"
            ]
        }
    }
    
    # 如果找不到对应模块，返回默认内容
    return content_map.get(module_name, {
        "scientific_basis": "该模块的科学原理说明正在完善中...",
        "design_philosophy": "设计理念说明正在完善中...",
        "mathematical_principle": "数学原理说明正在完善中...",
        "references": ["相关文献正在整理中..."]
    })

def register_callbacks(app):
    """
    注册所有科学提示框的回调函数
    """
    import dash
    from dash.dependencies import Input, Output, State, ALL
    from dash import ctx
    
    # 定义所有需要添加提示的模块
    modules = [
        ("multidim", "多维度分析"),
        ("network", "网络分析"),
        ("linchpin", "Linchpin靶点"),
        ("survival", "生存分析"),
        ("multiomics", "多组学整合"),
        ("closedloop", "ClosedLoop分析"),
        ("immune", "免疫微环境"),
        ("drug", "药物响应预测"),
        ("subtype", "分子分型"),
        ("metabolism", "代谢分析"),
        ("heterogeneity", "异质性分析")
    ]
    
    for tip_id, module_name in modules:
        # 显示/隐藏卡片
        @app.callback(
            [Output(f"card-{tip_id}", "style"),
             Output(f"backdrop-{tip_id}", "style")],
            [Input(f"open-{tip_id}", "n_clicks"),
             Input(f"close-{tip_id}", "n_clicks"),
             Input(f"backdrop-{tip_id}", "n_clicks")],
            [State(f"card-{tip_id}", "style"),
             State(f"backdrop-{tip_id}", "style")],
            prevent_initial_call=True
        )
        def toggle_card(open_clicks, close_clicks, backdrop_clicks, card_style, backdrop_style):
            if ctx.triggered_id and "open" in ctx.triggered_id:
                # 显示卡片
                card_style = card_style.copy() if card_style else {}
                backdrop_style = backdrop_style.copy() if backdrop_style else {}
                card_style["display"] = "block"
                backdrop_style["display"] = "block"
                return card_style, backdrop_style
            else:
                # 隐藏卡片
                card_style = card_style.copy() if card_style else {}
                backdrop_style = backdrop_style.copy() if backdrop_style else {}
                card_style["display"] = "none"
                backdrop_style["display"] = "none"
                return card_style, backdrop_style
        
        # 选项卡内容切换
        @app.callback(
            Output(f"tab-content-{tip_id}", "children"),
            [Input(f"tabs-{tip_id}", "active_tab")],
            [State(f"content-store-{tip_id}", "data")]
        )
        def render_tab_content(active_tab, content):
            if not content:
                return html.Div()
            
            if active_tab == "scientific-basis":
                return html.Div([
                    html.Div(
                        content["scientific_basis"],
                        className="scientific-content-text",
                        style={
                            "fontSize": "1rem",
                            "lineHeight": "1.8",
                            "color": "#2c3e50",
                            "textAlign": "justify"
                        }
                    )
                ])
            elif active_tab == "design-philosophy":
                return html.Div([
                    html.Div(
                        content["design_philosophy"],
                        className="scientific-content-text",
                        style={
                            "fontSize": "1rem",
                            "lineHeight": "1.8",
                            "color": "#2c3e50",
                            "textAlign": "justify"
                        }
                    )
                ])
            elif active_tab == "mathematical-principle":
                return html.Div([
                    dcc.Markdown(
                        content["mathematical_principle"],
                        dangerously_allow_html=True,
                        className="math-content",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "padding": "20px",
                            "borderRadius": "8px",
                            "border": "1px solid #e9ecef",
                            "fontSize": "0.95rem",
                            "lineHeight": "1.6",
                            "fontFamily": "'Courier New', monospace"
                        }
                    )
                ])
            elif active_tab == "references":
                return html.Div([
                    html.Ol([
                        html.Li(
                            ref,
                            style={
                                "marginBottom": "10px",
                                "fontSize": "0.9rem",
                                "lineHeight": "1.6",
                                "color": "#495057"
                            }
                        )
                        for ref in content["references"]
                    ], style={"paddingLeft": "20px"})
                ])
            
            return html.Div()

# 样式定义
SCIENTIFIC_TIP_STYLE = """
/* 按钮样式 */
.scientific-tip-button {
    position: relative;
    top: -2px;
    transition: all 0.3s ease;
}

.scientific-tip-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3) !important;
    background-color: #138496 !important;
}

.scientific-tip-button:active {
    transform: translateY(0);
}

/* 卡片动画 */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translate(-50%, -48%);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

/* 背景遮罩 */
.scientific-tip-backdrop {
    animation: fadeIn 0.3s ease-out;
    cursor: pointer;
}

/* 卡片样式 */
.scientific-tip-card {
    animation: slideIn 0.3s ease-out;
}

/* 关闭按钮 */
.scientific-tip-close:hover {
    color: #343a40 !important;
    transform: scale(1.1);
}

/* 选项卡样式 */
.nav-tabs {
    border-bottom: 2px solid #e9ecef;
}

.nav-tabs .nav-link {
    border: none;
    border-bottom: 3px solid transparent;
    background: none;
    color: #6c757d;
    font-weight: 500;
    padding: 10px 20px;
    transition: all 0.3s ease;
}

.nav-tabs .nav-link:hover {
    border-bottom-color: #e9ecef;
    color: #495057;
}

.nav-tabs .nav-link.active {
    background: none;
    border: none;
    border-bottom: 3px solid #007bff;
    color: #007bff;
}

/* 内容样式 */
.scientific-content-text {
    animation: fadeIn 0.5s ease-out;
}

.math-content {
    font-family: 'Courier New', monospace;
    line-height: 1.6;
    overflow-x: auto;
}

.math-content pre {
    margin: 10px 0;
    padding: 10px;
    background: #f1f3f5;
    border-radius: 4px;
    overflow-x: auto;
}

.math-content code {
    background: #e9ecef;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}

/* 滚动条样式 */
.scientific-card-body::-webkit-scrollbar {
    width: 8px;
}

.scientific-card-body::-webkit-scrollbar-track {
    background: #f1f3f5;
    border-radius: 4px;
}

.scientific-card-body::-webkit-scrollbar-thumb {
    background: #ced4da;
    border-radius: 4px;
}

.scientific-card-body::-webkit-scrollbar-thumb:hover {
    background: #adb5bd;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .scientific-tip-card {
        width: 95% !important;
        top: 5% !important;
        transform: translateX(-50%) !important;
        max-height: 90vh;
    }
    
    .scientific-card-body {
        max-height: 70vh !important;
    }
    
    .nav-tabs .nav-link {
        padding: 8px 12px;
        font-size: 0.9rem;
    }
}
"""