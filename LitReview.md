---
author:
- José L. Ulloa, PhD
bibliography:
- ../fMRI_BreastDCEMRI.bib
date: 2024-01-24
title: Algorithm and software development to analyse Functional Breast
  DCE-MRI dataset
---

# Scope of Work[^1]

1.  **Literature review:** Focus on reviewing the state of the art of
    image registration techniques applied to breast DCE-MRI and its
    application to morphology assessment of tumour changes. Deliverables
    are:

    -   Summary report.

    -   Workflow for the analysis pipeline.

    -   Mock-up of the graphical interface to analyse the data.

2.  **Validate registration strategy:** Based on the literature review,
    an improved registration algorithm will be developed and coded in
    Python. A basic interactive interface will be developed to allow
    testing of the algorithm and its variation with real data.
    Deliverables are:

    -   Summary report detailing the theory basis of the algorithm,
        details of the code implementation and examples validating the
        output against existing algorithms.

    -   Access to the source code.

    -   Instructions on how to test it with real data.

3.  **Tumour segmentation and parametric maps validated on real data:**
    By using the deformation maps to estimate tumour heterogeneity and
    the pixel-by-pixel functional parameters derived from the images, a
    set of tumour functional biomarkers will be added to the software
    tool. Deliverables are:

    -   Summary report detailing the calculation method to obtain the
        parametric maps, statistics relevant to characterise tumour
        changes, and examples validating the calculations.

    -   Access to the source code.

    -   Instructions on how to test it with real data.

4.  **Wrap it up in a GUI:** As defined in the kick-off meeting
    (04/01/2024), the focus will be to develop an extension that can be
    plugged into existing software, such as Slicer. On this final
    milestone, the codes developed to register and derive parametric
    maps will be wrapped into the form of an extension installable in
    Slicer (or equivalent). The source code will be available as open
    source in a GitHub repository. Deliverables are:

    -   Slicer (or equivalent) installable module.

    -   Access to the GitHub repository with the source code and user
        guide instructions.

    -   Examples validating the tool in the form of a video tutorial.

# Milestone #1

This part of the work has been dedicated to: identify key references
about methodology and tools to process functional breast DCE-MRI and
longitudinal analysis to assess its value as predictor of treatment
response; evaluate existing software tools to process the data which can
be used as the starting point to develop our own extension that best fit
the purpose of the study; and propose a preliminary analysis pipeline to
automate the data processing. The following subsections summarise the
main outcomes of this milestone.

## Literature review on image registration techniques applied to functional breast DCE-MRI {#LitReview}

In the domain of breast dynamic contrast-enhanced magnetic resonance
imaging (DCE-MRI), the efficacy of image registration techniques stands
as a critical determinant for precise automated and semi-automated
analyses [@thakran_impact_2022]. This literature review is based on a
subset of relevant literature associated to image registration and
quantification methodologies tailored to breast DCE-MRI, emphasising
their role as predictive indicators of treatment response.

Most of the work on functional breast DCE-MRI as a predictive biomarker
of tumour therapy response have focused on the response to chemotherapy
treatment
[@panthi_assessment_2023; @thakran_impact_2022; @jahani_prediction_2019; @jafri_optimized_2014; @ashraf_breast_2015],
but relatively few have evaluated this imaging technique as a predictor
of radiotherapy response in breast tumours
[@vasmel_dynamic_2022; @weinfurtner_mri_2022; @wang_assessment_2016; @mouawad_dce-mri_2020].
Despite the expected differences in tumour morphology caused by these
two families of treatment, the way these changes are assessed through
imaging are essentially the same, as well as the image pre-processing
steps. The main differences will be at the level of interpretation of
the changes in the parametric response maps. For example, in
chemotherapy, one of the expected morphological response is tumour
shrinkage e.g. [@hylton_locally_2012; @henderson_breast_2018], while the
opposite has been reported for radiotherapy, specially when assessed
early after the treatment [@vasmel_dynamic_2022]. Although this effect
is likely to be an inflammatory response to the treatment
[@wang_assessment_2016], from the analysis methodology point of view, it
highlights the importance of an holistic approach combining different
measurements to understand how they interact. It therefore requires that
any analysis platform must offer flexibility to combine these
measurements in different ways, as well as, should allow to ensemble
methods as it helps boosting their performance adding more value to the
analyses [@muenzing_dirboostalgorithm_2014].

Since its creation in 1998, [3DSlicer](https://www.slicer.org/) has
played an important role in a variety of clinical research. It is a free
and open source software package oriented to medical image analysis, has
a modular organisation that allows the addition of new functionality,
providing analysis capabilities such as image registration,
pharmacokinetic modelling and parametric mapping, among many others
[@fedorov_3d_2012; @kikinis_3d_2014]. Together with that, it offers a
friendly graphical user interface (GUI) that allows reviewing and
labelling images from different sources, display arbitrarily oriented
image slices, build surface models from image labels, and hardware
accelerated volume rendering [@kapur_increasing_2016]. These advantages
makes it the platform of choice to work on this project. Specifically,
it provides the starting points to develop a GUI-based tool to
pre-process, register and create parametric response maps of functional
breast DCE-MRI dataset. It provides all the functionalities to focus on
the algorithm development, with no need to invest time in developing
data management tools, as it already has embedded modules to handle
DICOM data and the visualisation of 3D dataset.

Regarding the analysis pipeline of oncology imaging studies, the
standard methodology is to compare tumour tissue before and after
treatment. To do so, patients should undergo the MRI scan at least
twice: before and after treatment. On each visit, they can have multiple
scans, and in most cases, between scans, a bolus injection of exogenous
contrast agent is injected to highlight tumour function by mapping the
contrast uptake. Given the images before and after contrast injection,
as well as between visits, are not aligned (either because of contrast
changes, motion caused by patient movement, cardiac and respiratory
motion, acquisition artefacts, etc.) to map the differences in tumour
morphology before and after treatment is not just to take the arithmetic
difference of the images or derived parameters, but prior to that is
necessary to map the tumour into a common space where every voxel
represents the same location in different images. This process can be
done manually, where an expert radiologist delineate the tumour tissue
and other fiducial marker on each image, and then the differences are
mapped into a region of interest that can be translated into the
different images. Or, it can be done automatically where alignment of
the images between different sequences and different scanning sessions
is performed by an algorithm, such as rigid, affine or deformable
methods [@avants_symmetric_2008; @ou_DRAMMS_2011; @klein_elastix_2010].
The former method offers advantages in the sense that minimises the
natural operator variability when manually delineating a region of
interest (ROI), because it is a repeatable and reproducible methodology,
and mainly depends on the image quality and MRI acquisition parameters.
But more importantly, an automated registration algorithm produces a
deformation map (a mathematical function that allows translating one
image into the spatial domain of the other) that provides information
about tumour heterogeneity, which on itself has been reported as a
useful predictor biomarker of tumour response
[@jahani_prediction_2019; @wang_assessment_2016; @vasmel_dynamic_2022; @li_tumour_2014].

As highlighted by recent studies
[@jahani_prediction_2019; @thakran_impact_2022], independent on the
registration algorithm used, ensuring the images are correctly aligned
before quantifying the parametric response maps is key for the accuracy
of the derived quantitative measurements. Based on the results reported
by [@thakran_impact_2022], from the comparison among 6 of the most
commonly used registration algorithms, ANTs [@avants_symmetric_2008] and
DRAMMS [@ou_DRAMMS_2011] show best performance as indicated not only by
the residual errors, which not necessarily ensures accuracy
[@rohlfing_image_2012], but also as compared against gold-standards
derived from expert key landmarks labelled by expert radiologist.
Therefore, on this initial work, we are going to base the development on
these two algorithms, starting from the already available Slicer
implementations [SlicerANTs](https://github.com/netstim/SlicerANTs) and
[SlicerBreast_DCEMRI_FTV](https://github.com/rnadkarni2/SlicerBreast_DCEMRI_FTV).

Both algorithms have many configurable parameters, and there is no a
single combination that ensures accurate results. They depend on
multiple parameters, such as image modality, image contrast, acquisition
parameters, anatomy of interest, etc. But fortunately, there are studies
that provide some clues on which sets of parameters should be considered
to change when optimising or tuning the algorithm
[@mehrabian_deformable_2018], which will be our starting point to
evaluate these algorithms. Also, following [@thakran_impact_2022]
methodology, we are going to define key landmarks, included sections of
breast tumours, that will be evaluated by expert radiologist in a subset
of the images, those points will be used to validate the accuracy of the
registration algorithm tested.

Although the registration algorithm is the main outcome of the first
part of this project, the main aim of the project is to define a set of
parametric response maps that quantify tumour changes and how it
correlates with response to radiotherapy treatment. In appendix 1, there
is a summary of the key publications that report on PRMs. In milestone
#3, we are going to implement them and program interactive tools that
allow explore their behaviour and summarise relevant statistics.
Together with the mathematics defining each parameters, most of the work
on that milestone will be dedicated to generate adequate filters to
reduce noise, error traps that avoid singularities in the calculations
and semi-automated segmentation tools to highlight changes in tumour
tissue, avoiding confounders such as blood vessels or any other highly
vascular anatomies. As a basis. the following parameters will be
considered
[@panthi_assessment_2023; @vasmel_dynamic_2022; @jahani_prediction_2019; @yamaguchi_kinetic_2021; @musall_functional_2021; @li_predicting_2020]:

-   Deformation maps (Jacobian of the transformation) to quantify tumour
    heterogeneity

-   Signal Enhancement Ratio (SER) and its peak

-   Percentage Enhancement (PE) and its peak

-   Functional Tumour Volume (FTV), segmented based on enhancement
    patterns

-   Wash-In and Wash-Out Slopes (WIS, WOS)

## Proposed image registration workflow and analysis pipeline {#ImgRegWorkflow}

Data acquisition MRI protocol (only DCEMRI included). There are more
sequences, but for this stage, these are the relevant data we're going
to use

<figure id="fig01_ms01b_acquisiition_protocol">
<div class="center">
<img src="diagrams/Figure01_DCEMRI_Protocol.png" />
</div>
<figcaption>Data acquisition protocol. For each patient, there will be 2
scan sessions: Before treatment (Pre-treatment baseline) and after 6
weeks of treatment (Post-treatment). On each visit, a set of
high-spatial resolution (HSR) DCE-MRI scans will be acquired (among
others, but that are not relevant for this particular work). For each
session, there will be a total of 6 HSR DCE-MRI scans: 1 scan before
contrast injection (pre-contrast scan) and 5 after the bolus injection.
The post-contrast starts after a set of high-temporal low-spatial
DCE-MRI scans</figcaption>
</figure>

The data will be processed in [3D Slicer](https://www.slicer.org/), an
open-source multi-platform software to process medical imaging data and
that has available modules to pre-process, co-register and quantify
parametric maps from imaging data. This platform and tools are going to
be the basis for the development work to implement the data analysis
pipeline for this project (Figure
[2](#fig02_ms01b_analysis_workflow){reference-type="ref"
reference="fig02_ms01b_analysis_workflow"}):

1.  **Data Transfer:** All the data transferred will be handled in DICOM
    format, not only the input data from the scanners, but also the
    output data from the analyses. An on-demand Orthanc web server will
    be setup to enable data transfer. It will be usually off (to avoid
    unnecessary costs associated to the cloud infrastructure), but can
    easily be switched on whenever needed to transfer imaging data.
    Whenever is active, it can be accessed at
    [orthanc.scua.cl](http://orthanc.scua.cl)[^2].
    [Orthanc](https://www.orthanc-server.com/) is an open-source DICOM
    server that can work in tandem with online storage platforms, such
    as [S3 from Amazon Web Services](https://aws.amazon.com/s3/). As
    part of the development work, a cost-effective long-term solution is
    going to be explored.

2.  **Data pre-processing:** Data is going to be pre-processed to
    correct some variations caused by field inhomogeneities and other
    artefacts, as well as contribute to a more accurate registration
    [@thakran_impact_2022]. Bias-normalisation will be performed by
    using the N4ITK [@tustison_n4itk_2010] algorithm, available in
    Slicer
    [(`Modules->Filtering->N4ITK MRI Bias Correction)`](https://slicer.readthedocs.io/en/5.6/user_guide/modules/n4itkbiasfieldcorrection.html).
    Histogram matching will be applied just before running the
    registration algorithm, using the pre-process option inside the
    [SlicerANTs extension](https://github.com/netstim/SlicerANTs).

3.  **Image Registration:** The efficacy of image registration
    techniques is critical to deliver precise automated and
    semi-automated analyses [@thakran_impact_2022]. Therefore, an
    important part of this work will be dedicated to optimise a
    registration algorithm to ensure correct alignment of the tumours
    when performing the longitudinal analyses. In Slicer, there are
    available implementations for the three main registration algorithms
    cited in the literature for processing function breast DCE-MRI data:
    [ANTs](https://github.com/netstim/SlicerANTs)
    [@thakran_impact_2022; @avants_symmetric_2008],
    [DRAMMS](https://github.com/rnadkarni2/SlicerBreast_DCEMRI_FTV)
    [@jahani_prediction_2019; @ou_DRAMMS_2011], and
    [Elastix](https://github.com/lassoan/SlicerElastix)
    [@mehrabian_deformable_2018; @klein_elastix_2010], so these codes
    will be used as the starting point for the method development.

4.  **Quantification of Parametric Response Maps (PRM)**: Following the
    literature
    [@vasmel_dynamic_2022; @panthi_assessment_2023; @jafri_optimized_2014],
    parametric response maps reporting the Signal Enhancement Ratio
    (SER), Peak Enhancement (PE) and their corresponding peaks values
    (peak SER and peak PE) will be used to derive Functional Tumour
    Volume (FTV). Based on the enhancement characteristics, the tumour
    will be segmented (semi-)automatically[^3], before deriving the
    parameters.

5.  **Data export:** The final stage is data export to DICOM format. In
    Slicer, all imaging data can easily be exported to DICOM. As part of
    the development work, we have code the corresponding module to add
    the segmentation masks into the exported datasets. The exported data
    will then be uploaded into the DICOM web server for sharing and
    review.

<figure id="fig02_ms01b_analysis_workflow">
<div class="center">
<img src="diagrams/Figure02_DCEMRI_Analysis.png" />
</div>
<figcaption>Data analysis workflow. Each dataset will be
<strong>uploaded</strong> into a lightweight DICOM server, from where
they will be loaded into Slicer. The analysis workflow leverages the
existing modules and extensions available in Slicer, part of the
development work will be to improve and extend them to fit the needs for
this project. Briefly, data will be <strong>pre-processed</strong> to
correct acquisition artefacts (mainly field inhomogeneities) using N4ITK
algorithm <span class="citation"
data-cites="tustison_n4itk_2010"></span> and improve registration
accuracy using histogram matching <span class="citation"
data-cites="golden_dynamic_2013"></span>. Data will then be
<strong>co-registered</strong> in two-stages to align intra-visit scans
and inter-visit dataset (see next section for details on the
registration pipeline). Once the data has been registered,
<strong>parametric maps</strong> will be derived and analysed following
<span class="citation" data-cites="jafri_optimized_2014"></span>. This
stage considers not only parameters calculations, but also tumour
segmentation (based on signal enhancement characteristics) as well as
quantifying differences between pre- and post- treatment scans. The
final stage includes <strong>exporting to DICOM</strong>, which is done
inside Slicer, and uploading the data into the DICOM server for further
clinical review and evaluation.</figcaption>
</figure>

### Registration strategy

The literature review in section [2.1](#LitReview){reference-type="ref"
reference="LitReview"}, explored cutting-edge image registration
methodologies tailored to breast DCE-MRI, with a particular focus on how
to implement them to assess longitudinally their application in
elucidating morphological changes within breast tumours. The problem of
co-registration is split in two sub-problems (Figure
[3](#fig03_ms01b_registration_pipeline){reference-type="ref"
reference="fig03_ms01b_registration_pipeline"}), based on the type of
motion to correct [@mehrabian_deformable_2018]:

-   **Intra-scan**: Registration is performed on the DCE-MRI scans.
    According to the protocol, each visit contains 6 High Spatial
    Resolution DCE-MRI: 1 before contrast injection (pre-contrast) and 5
    post-contrast on different timepoints after contrast injection.
    These 5 post-contrast will be aligned to the pre-contrast,
    considered as the baseline scan (although this can be evaluated and
    challenged during the method development stage). Independently of
    which scan is used as the reference (i.e. Fixed) image, at the end
    of the process, all the 6 DCE-MRI scan will be aligned and
    represented in a single image space. The change in contrast between
    images is the main source of differences that in this case needs to
    be corrected with the registration algorithm, also, minor movements,
    respiration and cardiac cycles contributes to misalignment.
    Therefore, the parameters have to be tuned to compensate these types
    of motions.

-   **Inter-scan**: Having all the series for a specific visit aligned
    to a single series, means that for each visit we have only one image
    space. Therefore, between visits only one spatial transformation is
    required to have all the dataset aligned to a single reference map.
    With that, we can define different sets of hyper-parameters for each
    stage, reflecting the different type of motions that dominates both
    cases. Deformations, changes in shapes and bulk motion are the main
    differences that in this case needs to be corrected with the
    registration algorithm. Therefore, the parameters have to be tuned
    to compensate these differences.

In both cases, the algorithm calculates rigid and affine transformations
before running into the deformable transform and operates on different
scales of the image, i.e. first resample the image to a very coarse
resolution, so it runs very quickly and aligns the larger anatomies,
then it moves sequentially to higher resolutions until it reaches the
original one. At this stage, it works aligning the smaller parts, like
small vessels and tumour sections. The registration algorithm has
configurable parameters to control the contribution of each of these
steps into the final results. Therefore, an important part of the
development work has to be dedicated to optimise and tune these
hyper-parameters [@mehrabian_deformable_2018]. Additionally, to improve
efficiency during the calculations, different image masking options will
be explored, in order to reduce the amount of processing data during
each iteration.

<figure id="fig03_ms01b_registration_pipeline">
<div class="center">
<img src="diagrams/Figure03_DCEMRI_Registration.png" />
</div>
<figcaption>Registation Strategy: Based on the types of motions observed
between scan on the same visit and between visits, the problem of
co-registration is split in two sub-problems. When registering images of
the same scan visit, but on different phases of the contrast uptake, the
main source of motion is the change in contrast, followed by minor (in
the case of breast images) displacements, respiratory and cardiac
movements. On the other hand, when registering images from different
visits, the sources and type of motion are mainly large deformations and
changes in shape. These differences requires separate the problems to
define optimum hyper-parameters sets that fit best each
one.</figcaption>
</figure>

## Drat Mockup Graphical User Interface (GUI) {#mockupGUI}

# Summary of key references

../SummaryKeyPublications/panthi_assessment_2023.tex

## Impact of deformable registration methods for prediction of RFS response to NAC in breast cancer: Results from the ISPY 1/ACRIN 6657 trial [@thakran_impact_2022]

### Purpose

-   To evaluate the effect of registration accuracy of six established
    deformable registration methods on the predictive value of extracted
    radiomic features when modeling RFS[^4] for women after NAC[^5] for
    locally advanced breast cancer

-   The following six deformable registration methods were assessed:

    1.  ANTs [(Advanced Normalisation
        Tools)](https://stnava.github.io/ANTs)

    2.  DRAMMS [(Deformable Registration via Attribute Matching and
        Mutual-Saliency
        Weighting)](https://github.com/ouyangming/DRAMMS)

    3.  ART [(Automatic registration
        toolbox)](https://www.nitrc.org/projects/art/)

    4.  NiftyReg [(Nifty
        Registration)](https://www.nitrc.org/projects/niftyreg/)

    5.  NMI-FFD [(Normalised Mutual Information - Free Form
        Deformation)](https://mirtk.github.io/)

    6.  SSD-FFD [(Statistical Shape and Deformation Analysis -
        FFD)](https://mirtk.github.io/)

-   To evaluate and compare the six deformable image registration
    methods based on 2,380 landmarks individually marked by two
    radiologists in an independent dataset of longitudinal breast MR
    scans.

### Population sample and procedure

-   Retrospective study on de-identified data from \"The Cancer Imaging
    Archive\"
    [(TCIA)](https://www.cancerimagingarchive.net/access-data/)

-   Patient population was a subset of patients with longitudinal breast
    DCE-MRI scans, publicly available at TCIA, from the ISPY1/ACRIN
    66577 trial.

-   Women enrolled in the study had T3 breast tumours measuring 3cm and
    received anthracycline-cyclophosphamide (AC) NAC

-   222 cases from ISPY1trial were included in the study, but after
    excluding 92 because image problems (see details below), the
    remainder 130 women that had DCE-MRI scans available from the first
    two visits in the ISPY1/ACRIN-6657 cohort were analysed

    -   15 cases were excluded due to low quality images

    -   65 cases were excluded due to incomplete clinical and imaging
        data

    -   12 cases were excluded due to incomplete image registration

-   RFS criteria was taken from STEEP [@hudis_proposal_2016] [^6]: time
    from the first chemotherapy cycle to the event (i.e., recurrence or
    death)

-   Final analysis included 130 women with 38 events from the
    ISPY1/ACRIN 66577 cohort for RFS analysis

-   pCR information was missing for 5 participants (leaving 125 patients
    for pCR analysis)

-   Overall tumor response rate for the study sample was about 28.5%

### Image acquisition and Data analysis

-   Imaging protocols are described according to the ISPY1/ACRIN 6657 in
    [@hylton_locally_2012]

-   MRI data were acquired on a 1.5T scanner with a breast-dedicated
    coil

-   Four longitudinal MRI examinations were performed at different time
    points during the therapy

-   To focus on the ability to predict likelihood of survival early in
    the course of the therapy, MRI scans from the first two visits were
    used:

    -   Baseline Scan: Four weeks before AC chemotherapy

    -   Early Treatment Scan: At least Two weeks after the 1st cycle of
        AC and before the 2nd cycle of AC

-   Prior to analyse the cohort for RFS, an independent \"test-retest\"
    sample of 14 subjects with retrospectively collected breast MR
    images, also publicly available by the ISPY/ACRIN 6657, were used to
    evaluate the registration accuracy in this study. These dataset was
    previously reported by [@ou_deformable_2015][^7] as used to assess
    DRAMMS, NMI-FFD and SSD-FFD registration methods (so it was used as
    positive control)

-   A total of 2,380 land- marks (median 78 (IQR:63.25-107.25) per
    patient) were marked and labeled at:

    -   breast boundaries

    -   nipples

    -   internal milk ducts

    -   chest walls

    -   glandular structures

    -   vessels

    -   tumors

    these expert-defined landmarks were used as gold-standard

-   The follow-up image was registered to the baseline image for each
    patient (median 17.5 (IQR:14-55.75) days apart)

-   This study complements [@ou_deformable_2015] in the sense it adds
    registration methods ANTs, ART and NiftyReg to compare accuracy
    against DRAMMS, NMI-FFD and SSD-FFD

-   To analyse the cohort for prediction of NAC RFS, FTV calculated at
    pre-treatment (FTV1) and early-treatment visits (FTV2) was available
    for each DCE- MRI scan

-   Image pre-processing:

    -   N3 bias-field normalisation to minimise intensity variations due
        to field inhomogeneities [@sled_nonparametric_1998][^8]

    -   Histogram matching applied between pre- and early-treatment
        images [@golden_dynamic_2013][^9]

Image Registration and hyper-parameter tuning:

-   Registration is used for spatial and anatomical alignment

-   Reference image is the pre-treatment baseline MRI

-   Registration algorithms are usually described by three main
    elements:

    1.  Deformation Model

    2.  Similarity Metric

    3.  Regularisation

-   This paper didn't focus on setting these (hyper-)parameters, but in
    comparing performance of the different algorithms. They used the
    (hyper-)parameter defined by the corresponding authors of each
    method, as those that provide them the most accurate alignment of
    longitudinal breast MR images (see details on each reference)

```{=html}
<!-- -->
```
-   Settings for the registration:

    ::: center
      Algorithm   Deformation mode/field         Similarity Metric                                  Regularisation
      ----------- ------------------------------ -------------------------------------------------- --------------------
      ANTs        Symmetric velocity (SyN)       Cross-correlation (CC)                             Gaussian Smoothing
      DRAMMS      Cubic B-spline                 Attribute-matching and Mutual-saliency-weighting   Bending-Energy
      ART         Non-parametric, homeomorphic   CC                                                 Gaussian Smoothing
      NiftyReg    Cubic B-spline                 NMI                                                Bending-Energy
      NMI-FFD     Cubic B-spline                 Normalised Mutual Information (NMI)                Bending-Energy
      SSD-FFD     Cubic B-spline                 Statistical Shape Deformation (SSD)                Bending-Energy

      : Table S1 from Supplementary Material
    :::

-   One big difference between ANTs and the other algorithms is that the
    latter doesn't use one image as reference (i.e doesn't transform one
    into the other's space), instead, by deforming both, it
    symmetrically finds a \"midpoint\" between the images which is used
    as the template.

-   NiftyReg performs both, global registration by using the
    block-matching technique, and local registration by cubic B-splines

-   Registration accuracy was measured by the Euclidean distance between
    landmarks. So they define the inter-expert landmark and
    algorithm-to-expert $i-$th landmark difference as follows:
    $$\begin{aligned}
    \textit{inter-expert}  = & d(y_{1i}, y_{2i}), & i=1,2,3,...,k \\
    \textit{algorithm-to-expert}  = & \frac{d(y_{3i}, y_{1i}) + d(y_{3i},y_{2i})}{2}, & i=1,2,3,...,k
    \end{aligned}$$

Parametric Response maps (PRM) and radiomic features for prediction of
RFS

-   Each DCE-MRI dataset consisted of 3 phases: Pre-contrast ($t_0$),
    early phase ($t_1$) and late phase ($t_2$)

-   Signal Intensity ($S(t)$) map was derived for each voxel on each
    time point

-   Four voxel-wise (e.g. voxel with coordinates $\vec{x}$) kinetic
    features were calculated from the 3 timepoints, for both pre- and
    pos-treatment scans, as defined in [@jahani_prediction_2019]:

    -   Peak Enhancement (PE):
        $$PE(\vec{x})=\max_{t=t_{PE}}\frac{I(\vec{x},t) - I(\vec{x},t_0)}{I(\vec{x},t_0)}$$

    -   Signal Enhancement Ratio (SER):
        $$SER(\vec{x}) = \frac{I(\vec{x},t_2)-I(\vec{x},t_0)}{I(\vec{x},t_1)-I(\vec{x},t_0)}$$

    -   Wash-in Slope (WIS): $$WIS(\vec{x})=\begin{cases}
        \frac{PE(\vec{x})}{t_{PE}-t_0} & \text{if }t_{PE}\neq 0 \\
        0 & \text{otherwise}
        \end{cases}$$

    -   Wash-out Slope (WOS): $$WOS(\vec{x})=\begin{cases}
        \frac{I(\vec{x},t_2)-I(\vec{x},t_1)}{t_{2}-t_{PE}} & \text{if }t_{2}\neq t_{PE} \\
        0 & \text{otherwise}
        \end{cases}$$

-   Difference between the kinetic feature maps from pre- and
    early-treatment MR images without registration was also calculated.

-   For higher accuracy, images were resampled to 1mm

-   Rotation variant LBP[^10] was used (**why??**) and a total of 27
    neighbours were considered for computation of LBP

-   Linear Interpolation was used for the MR images

-   104 radiomic features were extracted from each without registered
    kinetic features map, using the publicly available software, Cancer
    Phenomics Toolkit [(CaPTk)](https://www.med.upenn.edu/cbica/captk/)
    (see table [1](#table_s2){reference-type="ref" reference="table_s2"}
    that replicates Table S2 from supplementary material)

-   **This part don't understand what/how they did it:** applied
    principal component (PC) analysis to the 104-dimensional feature
    vector after calculating the z-score, and retained the first four
    PCs for modelling (i.e., one covariate for every 10 events in our
    cohort)

-   Transformation field derived from the image registration was used to
    quantify voxel scale changes between visits. This method is critical
    to understand how the comparison was made, so it is summarised below
    in a specific subsection

### Parametric Response Maps (PRM) computation methodology

-   **PRM is change between visits of a kinetic feature**

-   Corresponding voxels from maps between pre- and early-treatment
    visits must be determined to quantify voxel scale changes between
    visits.

-   Transformation fields derived from the registration algorithms are
    used to construct a voxel-wise map of change in a given kinetic
    feature (i.e. PRM)

-   These transformation fields warp the kinetic maps obtained from
    early-treatment MR images, i.e. for a voxel $\vec{x}$ in the
    pre-treatment image, there is a corresponding voxel from the
    treatment image that is warped to $\vec{x}$, i.e. $T_{12}(\vec{x})$

-   For a given kinetic feature ($KF$) (i.e. one of PE, SER, WIS or WOS)
    computed at pre- or early treatment visit ($KF_1$ or $KF_2$,
    respectively), the PRM value at each voxel $\vec{x}$ is calculated
    as:
    $$PRM(\vec{x}) = \textit{Jacobian}\biggr( KF_2(T_{12}(\vec{x})) - KF_1(\vec{x})\biggl)$$
    where *Jacobian* is the proportional volume change at $\vec{x}$
    between pre- and early-treatment visits

-   The Jacobian scales the value when a voxel in one image is the
    larger or smaller volume in the corresponding image.

-   Kinetic features and corresponding PRMs were only measured within
    the tumour

-   SER method was used to analyse DCE-MR images and **segment FTVs** on
    each visit (i.e. FTV1 and FTV2)

-   Similar to the unregistered data, 104 radiomic features were
    extracted from each PRM kinetic map, using CaPTK.

-   Also PC analysis was used to reduce dimensionality from 104 to 4
    (see previous sub-section)

### Statistical Analysis

-   The p-value of 0.05 cutoff was used to indicate statistical
    significance throughout the study

-   Cox proportional hazards regression was used to model 5-year RFS for
    each set of covariates, comparing eight models:

    1.  Model with the baseline covariates of age, race, and hormone
        receptor status (model F1)

    2.  Model F1 plus FTV at the early-treatment visit (FTV2) (model F2)

    3.  Model F2 plus radiomic feature without registration (model F3)

    4.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from ANTs Registration method

    5.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from DRAMMS Registration method

    6.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from ART Registration method

    7.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from NiftyReg Registration method

    8.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from SSD-FFD Registration method

    9.  Covariates in F2 with the addition of the radiomic feature PCs
        derived from NMI-FFD Registration method

-   C-statistic (see e.g. [Uno et al.
    2011](https://onlinelibrary.wiley.com/doi/10.1002/sim.4154)) was
    calculated both on the full models as well as 3-fold
    cross-validation averaged over 100 replicates.

-   Full models were used to generate KM plots

-   Log-rank p-value was used for estimating significance of KM
    separation and hazard ratios (HR) in Cox modelling

-   Each subject's risk signature was dichotomised at the median into
    high- and low-risk groups

-   To obtain a predicted risk score, the risk signature of each subject
    was defined as that subject's values of the covariates in a given
    model (i.e. age, race, hormone receptor status, FTV2, and selected
    features), weighted by the corresponding coefficients of those
    covariates in the model.

-   A randomisation test to calculate a p-value versus the null
    hypothesis that the improvement in the C-statistic, obtained by
    adding the radiomic data, was due only to chance. This was done for
    both full-model and 3-cross-validated with 100 repetitions
    C-statistic.

### Main Results

-   Baseline model F1:Age, Race, and Hormone-receptor-status, had a 0.54
    C-statistic

-   Model F2: baseline + FTV at early treatment visit (FTV2), had 0.63
    C-statistic

-   The F2+ANTs had the highest C- statistic (0.72), with the smallest
    landmark differences (5.40±4.40mm) as compared to other models.

-   The KM curve for model F2 gave p=0.004 for separation between women
    above and below the median hazard compared to the model F1(p=0.31).

-   ANTs registration method shows best accuracy in registering the
    longitudinal breast MR images as evidenced by the smallest landmark
    differences and being closest to the inter-expert differences

-   A models augmented with radiomic features, also achieved significant
    KM curve separation (p\<0.001). except the F2+ART model.

-   The framework of the current study consists of:

    -   Robust registration (Just by adding registration, PRM feature
        performance was improved, and further improvements were achieved
        by using more accurate registration methods, such as ANTs and
        DRAMMS)

    -   Voxel-wise changes of PRMs of kinetic features

    -   Radiomic feature and principal component analysis provide
        statistically significant improvements over previous similar
        analyses in predicting RFS

-   Some limitations of the study and future work:

    -   Relatively small sample size (n=130) and small number of events
        for RFS analysis

    -   An extension of this study can be done by applying these
        analyses to longitudinal images at mid- and late- treatment time
        points (it may help to better characterise heterogeneous tumor
        responses and the effects of treatment over time)

    -   Accuracy of these registration methods to be tested for large
        anatomical variabilities or imaging device differences (e.g.,
        2-D ultrasound to 3-D MRI)

### Conclusions

-   Incorporating image registration in quantifying changes in tumor
    heterogeneity during NAC can improve prediction of RFS.

-   Improvement in the registration process results in further
    improvements in the performance of PRM radiomic features when
    predicting RFS.

-   Radiomic features of PRM maps derived from warping the DCE-MRI
    kinetic maps using ANTs registration method further improved the
    early prediction of RFS (survival during NAC) as compared to other
    methods.

### Notes

-   This statement in the discussion section, confirms what I thought,
    that indeed some of the previous studies didn't use registration at
    all:

    > Several studies re-ported for prediction of RFS without
    > integration of image registration \[39--41\]

-   **IMPORTANT!!:** Other registration methods such as DROP, HAMMER,
    Plastimatch, and MIND might be tested

-   Registration accuracy can be further improved by utilising multiple
    registration methods in a meta-analysis framework, such as:

    -   A combination of ANTs and DRAMMS in a multi-atlas labelling
        framework [@doshi_muse_2016]

    -   A combination of ANTs, NiftyReg, and DROP which showed
        significantly reduced registration errors in pulmonary images
        [@muenzing_dirboostalgorithm_2014]

-   A workflow like to one proposed in this paper seems a reasonable
    starting point (see Figure
    [\[fig3_thakran\]](#fig3_thakran){reference-type="ref"
    reference="fig3_thakran"}).

    ::: center
    ![This is figure 3 from [@thakran_impact_2022]. It shows the outline
    of the process using different deformable image registration
    methods.](../imgs/Figure_3_Thakran_2022.jpg)

    []{#fig3_thakran label="fig3_thakran"}
    :::

::: center
::: {#table_s2}
  \#   Features                                            
  ---- --------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  1    Intensity                                           Coefficient of variation, Energy, Inter-Quartile Range, Kurtosis, Maximum, Mean, Mean absolute deviation, Median, Median absolute deviation, Minimum, Mode, Ninetieth percentile, Quartile coefficient of variation, Range, Root mean square, Skewness, Standard deviation, Sum, Tenth percentile, Variance
  2    Histrogram                                          Coefficient of variation, Energy, Entropy, Fifth Percentile, Fifth Percentile Mean, Inter-Quartile Range, Kurtosis, Maximum, Mean, Mean Absolute Deviation, Median, Median Absolute Deviation, Minimum, Mode, Ninetieth Percentile, Ninety Fifth Percentile, Ninety Fifth Percentile Mean, Quartile Coefficient Of Variation, Range, Robust Mean Absolute Deviation 1090, Root Mean Square, Seventy Fifth Percentile, Skewness, Standard Deviation, Sum, Tenth Percentile, Twenty Fifth Percentile, Uniformity, Variance
  3    Morophology                                         Eccentricity, Ellipse Diameter_Axis-0, Ellipse Diameter_Axis-1, Ellipse Diameter_Axis-2, Elongation, Equivalent Spherical Perimeter, Equivalent Spherical Radius, Flatness, Largest Component Size, Number Of Pixels, Perimeter, Physical Size, Roundness
  4    Gray Level co-occurrence Matrix (GLCM)              Auto Correlation, Cluster Prominence, Cluster Shade, Contrast, Correlation, Energy, Entropy, Homogeneity
  5    Gray Level Run length Matrix (GLRLM)                Grey Level Non-uniformity, High Grey Level Run Emphasis, Long Run Emphasis, Long Run High Grey Level Emphasis, Long Run Low Grey Level Emphasis, Low Grey Level Run Emphasis, Run Length Non-uniformity, Short Run Emphasis, Short Run High Grey Level Emphasis, Short Run Low Grey Level Emphasis
  6    Gray Level Size Zone Matrix (GLSZM)                 Grey Level Mean, Grey Level Non Uniformity, Grey Level Non Uniformity Normalised, Grey Level Variance, High Grey Level Emphasis, Large Zone Emphasis, Large Zone High Grey Level Emphasis, Large Zone Low Grey Level Emphasis, Low Grey Level Emphasis, Small Zone Emphasis, Small Zone High Grey Level Emphasis, Small Zone Low Grey Level Emphasis, Zone Percentage, Zone Size Entropy, Zone Size Mean, Zone Size Non Uniformity, Zone Size None Uniformity Normalised, Zone Size Variance
  7    Neighbourhood Gray Tone Difference Matrix (NGTDM)   Busyness, Coarseness, Complexity, Contrast, Strength
  8    Structural                                          LBP

  : Table S2 from supplementary material - List of the 104 radiomic
  features extracted
:::
:::

## DCE and DW MRI for response after single dose NA-PBI (irradiation) [@vasmel_dynamic_2022]

### Purpose

-   To evaluate changes in DCE and DW MRI scans acquired before and (up
    to 6 months) after single-dose ablative NA-PBI [^11]

-   To explore the relation between semi-quantitative MRI parameters and
    radiologic and pathologic responses

### Population sample and prrocedure

-   36 women with low-risk breast cancer (median age 65y, range 51-78y)

-   Median largest tumour diameter (LD) at baseline MRI was 13mm (range
    5-20mm)

-   All patients had an estrogen receptor-positive and human epidermal
    growth factor receptor 2-negative tumor

### Image acquisition and Data analysis

-   Patients were scanned in prone position on a 3.0T Ingenia (Philips)
    MRI scanner and a dedicated 16-ch breast coil

-   Up to 6 scans were performed on each patient: before radiation
    therapy (BL scan) and after therapy at 1 week, 2, 4, 6 and 8 months
    (this last one, only in some cases)

-   Scan protocol comprised:

    -   DW-MRI series (b-values=\[0, 150, 800\] s/mm$^2$, single-shot
        EPI, ADC calculated from mono-exponential fit)

    -   High-temporal/low spatial resolution 3D T1W DCE-MRI series
        (referred as High Temporal): 17 rapid full 3D volumes during the
        first 90s post-contrast injection (Gadovist, 0.1mL/kg at 1mL/s)

    -   Low-temporal/high-spatial resolution 3D T1W DCE-MRI series
        (referred as High Spatial): 6 full 3D volumes, the first
        acquired before contrast injection and the remaining 5, 5min
        straight after the High-Temporal (i.e. 6.5min after contrast
        injection)

    -   Both DCE-MRI series were acquired with a T1W FFE (spoiled),
        spectral attenuated IR fat-suppressed

-   Clinical response assessment was performed manually by expert
    radiologists at each scan after NA-PBI

-   MRI scans were scored as **radiologic complete response** (i.e.
    absence of both pathologic contrast enhancement and diffusion
    restriction) or **no radiologic complete response**

-   Pathologic response was evaluated on biopsies and classified as:

    -   **pCR:** no residual tumour cells

    -   **Near pCR:** \<10% residual tumour cells

    -   **Partial response:** 10%-50% residual tumour cells

    -   **Stable disease:** \>50% residual tumour cells

    -   **No evidence of responde:** According to European Society of
        Breast Cancer Specialists criteria

-   Gross tumor volume (GTV) was delineated manually on the first
    post-contrast image of the High-Spatial DCE BL MRI (i.e. before
    NA-PBI)

-   Onset of contrast wash-in was measured in the aorta (fixed ROI
    placed in the descending aorta in the High Temporal DCE-MRI at each
    scan visit)

-   **Rigid registration**
    [(Elastix)](https://elastix.lumc.nl/)[@klein_elastix_2010], was used
    to transform GTV delineation from BL to post-treatment MRI scans, as
    well as to correct motion of intra- and inter- DCE series

-   After registration, the final GTV-ROIs were dilated with 1-voxel
    margin to account inaccuracies

-   Geometric distortions in the DWI series were corrected using
    deformable registration using B-spline transform. As a reference
    target was used the High-spatial DCE series [@takatsu_novel_2019]

-   MRI scan affected by imaging artefacts (e.g. failed fat
    suppression), scans where GTV delineation could not be transferred,
    and DW series that could not be registered correctly to the DCE
    series were excluded.

-   Analyses were implemented in Matlab

-   Semi-quantitative parameters from the **High-Temporal Series**:

    -   Time to enhancement (TTE): Time difference between contrast
        reaching the aorta and the tumour:
        $$TTE = t_{tumour} - t_{aorta}$$ where $t_{aorta}$ is the first
        timepoint with $\geq$`<!-- -->`{=html}100% increase in median
        relative enhancement (RE) within the aorta and $t_{tumour}$, the
        first timepoint with $geq$`<!-- -->`{=html}50% increase in the
        90th percentile RE within the GTV-ROI. If $t_{tumour}$ didn't
        reach the threshold, it was set to the time of the last
        High-Temporal DCE + 5 seconds

    -   1-min relative enhancement ($RE_{1min}$), defined as the 90th
        percentile RE value in the GTV-ROI at 1min after enhancement of
        the aorta $$\label{re_calc}
        RE(t) = \frac{SI(t)-SI(0)}{SI(0)} \times 100\%$$ where $SI$ is
        the signal intensity, $t=0$ the pre-contrast injection image,
        $t>0$ the post-contrast injection images. A Gaussian filter
        ($3\times3\times3$ voxels, $\sigma=0.5$) was applied to reduce
        noise

-   Semi-quantitative parameters from the **High-Spatial Series**:

    -   Percentage of enhancing voxels (%EV), defined as the percentage
        of voxels within the GTV-ROI with \>100% RE at the first
        post-contrast image

    -   Relative distribution of washout curve types for enhancing
        voxels, calculated from voxel-wise RE difference between the
        first and last post-contrast injection images and defined as:
        $$\begin{aligned}
        \mbox{Type 1}&: &\geq +10\% RE \rightarrow \mbox{Low probability of malignancy}\\
        \mbox{Type 2}&: & \in [-10\%; +10\%] RE \rightarrow \mbox{Intermediate probability of malignancy}\\
        \mbox{Type 3}&: &\leq -10\% RE \rightarrow \mbox{High probability of malignancy} 
        \end{aligned}$$ RE was calculated using equation
        [\[re_calc\]](#re_calc){reference-type="ref"
        reference="re_calc"}. Unlike the High-Temporal series, no
        Gaussian filter was applied on these series

-   Semi-quantitative parameters from the **DW Series**:

    -   Median ADC value

### Statistical Analysis

-   Because of the small number of patients, only descriptive statistics
    (median and interquartile range \[IQR\]) was used to analyse the
    semi-quantitative parameters

### Main Results

-   Enhancement increased 1 week after NA-PBI, i.e. BL vs 1wk median:

    -   TTE: 15s vs 10s

    -   $RE_{1min}$: 161% vs 197%

    -   %EV: 47% vs 67%

-   Enhancement decreased from 2 months onward, i.e. 6 months median:

    -   TTE: 25s

    -   $RE_{1min}$: 86%

    -   %EV: 12%

-   Median ADC **increased** between BL and 6 months, from
    $0.83 \times 10^{-3}\mbox{mm}^2/s$ to
    $1.28 \times 10^{-3}\mbox{mm}^2/s$

### Conclusions

-   TTE, $RE_{1min}$, and %EV showed the most potential to differentiate
    between **radiologic** responses (i.e. radiologic complete
    responders and non-complete responders), as qualitatively assessed
    by breast radiologists, but were not statistically tested in this
    small cohort (i.e. couldn't be proved in this study)

-   TTE, $RE_{1min}$ at 6 months, and median ADC values at 4 and 6
    months, showed the most potential to differentiate between
    **pathologic** responses, but were not statistically tested in this
    small cohort (i.e. couldn't be proved in this study)

-   Changes in RE (Increase in %EV) and ADC (slight increase) 1 week
    after NA- PBI, indicate acute inflammation

-   From 2 to 6 months after radiation therapy, decrease in %EV and
    voxels with malignant washout curve (decrease), and Increase in ADC
    values indicate tumor regression (i.e. positive response to
    treatment)

-   The initial increase in $RE_{1min}$ at 1 week after radiation
    therapy was also observed in [@wang_assessment_2016] &
    [@mouawad_dce-mri_2020], but the conclusions on these studies are
    somehow contradictories:

    -   [@wang_assessment_2016] suggested the early response at 1wk can
        be used as a response biomarker

    -   [@mouawad_dce-mri_2020] the same early response demonstrated too
        much acute inflammatory effect to assess tumour response, they
        proposed to wait for the MRI scans at least 2.5wk after
        radiation therapy

    -   The 1wk signs of increased enhancement shown in this study most
        likely indicate radiation therapy-induced acute inflammation,
        confirming [@mouawad_dce-mri_2020].

-   ADC results are inline with those from the highest dose cohort
    reported in [@wang_assessment_2016], at 1wk post-treatment a slight
    increased was observed

-   Main drawback were the sample size, too small to drive statistical
    validation of the hypotheses, B0 map for inhomogeneity corrections
    and T1 map to derive quantitative DCE parameters (e.g. $K^{trans}$,
    $v_e$)

### Notes

-   This study mentions in the introduction, that semi-quantitative MRI
    is a predictor of pCR, but not in patients with low-risk breas
    cancer (see e.g. [@abramson_early_2013], [@galban_multi-site_2015],
    [@tudorica_early_2016], [@dietzel_automated_2017]).

-   It also highlights a couple of studies: [@wang_assessment_2016] &
    [@mouawad_dce-mri_2020], where semi-quantitative MRI has been
    applied to radiotherapy, but not showing good correlation to pCR.
    The former reported a dependency between radiation dose and
    direction of ADC change (calculated from DW-MRI in a sub-group
    analysis) and the latter, a significant change in $K^{trans}$ (i.e.
    quantitative DCE-MRI)

-   Something not seen in the previous studies reviewed was the onset
    measurement in the (descending) aorta of the contrast wash-in

-   An important conclusion regards the registration of the GTV-ROI, it
    is shown not very effective to evaluate changes in tumour volume and
    the presence of non-tumour tissue entering the ROI for cases where
    tumour shrank.

-   They suggest to use deformable registration for better adaptation of
    the GTV-ROI and to allow evaluation of tumour volume changes (which
    sound logical to me as well)

## Optimized Breast MRI FTV as a Biomarker of RFS Following NAC [@jafri_optimized_2014]

### Purpose

-   To evaluate optimal contrast kinetics thresh- olds for measuring
    functional tumor volume (FTV)

### Population sample and procedure

-   eRtrospective study of 64 patients (ages 29--72, median age of 48.6)
    undergoing neoadjuvant chemotherapy (NACT) for breast cancer

### Image acquisition and Data analysis

-   Manual delineation of tumours on each scan

### Statistical Analysis

-   

### Main Results

-   

### Conclusions

-   

### Notes

-   

## MRI response to Pre-Op SABR in ES ER/PR+ HER2- Breast Cancer correlate with Pathology Bed Cellularity [@weinfurtner_mri_2022]

### Purpose

-   To evaluates breast MRI response of ER/PR+ HER2- breast tumours to
    pre-operative SABR[^12] with pathologic response correlation

-   Retrospective study to evaluate radiologic-pathologic correlation of
    tumour response

-   Goal: Determine if MRI response to neoadjuvant SABR in early ER/PR+
    HER2- Breast Cancer correlates with pathologic response. If so, in
    the future, MRI response could guide treatment planning.

-   How does SABR work?:

    -   SABR targets a tumour volume from multiple angles by delivering
        large radiation doses over 1 to 5 sessions

    -   It delivers the radiation via a small cross-section radiation
        beam

-   The hypothesis is based on [@wang_assessment_2016] study, where
    results showed MRI correlation with radiation dose differences

-   Hypotheses:

    -   Tumour size reduction on MRI correlates with %TC[^13] in the
        surgical specimen

    -   Combined %TC and %TILs[^14] \"CelTIL\" score also correlates
        with tumour size reduction on MRI (To account for possible
        immune response effects)

    -   Change in BI-RADS descriptors on MRI from mass to focus,
        non-mass enhancement, or no residual enhancement as well as a
        change from fast to slower initial enhancement and from delayed
        earlier to later peak enhancement would result in smaller %TC at
        surgery

    -   Complete MRI response on the post-SABR MRI would correlate with
        pCR

-   There are plenty of evidence and studies evaluating MRI as a
    predictor of pre-operative NAC response:

    -   MRI-derived Tumour Volume Change correlates with Percent Tumour
        Cellularity in patients treated with NAC
        [@choi_evaluation_2018] - MRI data was analysed via CADSTREAM
        [@kurz_assessment_2009], a commercial software

    -   Mid-treatment response on MRI and complete MRI response at the
        final MRI were predictive of pCR at surgical pathology in
        patients undergoing NAC [@dave_neoadjuvant_2017] - MRI data was
        manually assessed and quantified by radiologists, using
        [modified RECIST](https://pubmed.ncbi.nlm.nih.gov/32050313/).

    -   Results from the ACRIN 6657 trial showed that evaluation of
        residual longest dimension of the tumor on breast MRI performed
        after NAC demonstrated the strongest correlation with pathology
        size compared to mammography and physical exam
        [@scheel_mri_2018] - They used the method described by
        [@hylton_locally_2012] to analyse the MRI data

### Population sample and procedure

-   Retrospective study from a Phase 2 single institution trial off SABR
    for ER/PR+ HER2- Breast Cancer

-   19 pre-operative SABR-treated ER/PR+ HER2- breast cancers

-   Inclusion criteria of the Trial were:

    -   Female $\geq 50$yo

    -   Unifocal and invasive breast adenocarcinoma

    -   Tumour size $\leq 2$cm (based on [ASTRO updated consensus
        statement](https://www.practicalradonc.org/article/S1879-8500(16)30184-9/fulltext)).
        This size was determined from the baseline MRI who were
        clinically and radiologically lymph node-negative (defined as
        patients without suspicious lymph nodes on pre-treatment US or
        MRI, or patients with US-guided benign lymph node biopsy)

-   Exclusion criteria included:

    -   History of other invasive malignancies in the prior 5 years

    -   History of ipsilateral breast or thoracic radiotherapy

    -   Patients with mutation in BRCA1 and BRCA2 (based also on ASTRO
        consensus statement)

-   2 patients were excluded from the analysis, one withdrew the trial
    and the other had a baseline MRI deemed insufficient for review

-   Patients underwent baseline breast MRI, SABR (28.5 Gy in 3
    fractions), follow-up MRI 5 to 6 weeks post-SABR, and lumpectomy

### Image acquisition and Data analysis

-   Patients were scanned in prone position in a GE 1.5T Optima 450w MRI
    scanner using a 16ch double-breast array coil

-   Standard bilateral MRI acquisition protocol included:

    -   Axial pre-contrast 3D T1W SPGR sequence with parameters:

        -   Matrix size $512 \times 512$

        -   FOV $300 \times 300$cm

        -   Slice Thickness 1.5mm, no slice gap

    -   Axial pre-contrast T2W STIR sequence with parameters:

        -   TR=6835ms

        -   TE=24ms

        -   Matrix size: $512 \times 512$

        -   FOV $300 \times 300$cm

        -   Slice Thickness 3.0mm, no slice gap

    -   1 pre-contrast and 4 post-contrast (at 60 to 90 sec intervals)
        Axial FAT-sat 3D T1W SPGR sequence with parameters:

        -   Matrix size $512 \times 512$

        -   FOV $300 \times 300$cm

        -   Slice Thickness and slice spacing 1.5mm

        -   Flip Angle: 10deg

    -   0.1mmol/Kg gadobutrol (Gadavist) contrast was injected

-   Tumor size and BI-RADS[^15] descriptors on pre and post-SABR breast
    MRIs were compared to determine correlation with surgical specimen
    %TC

-   BL and post-SABR MRI were read by radiologist and reported following
    the standard of the American College of Radiology (ACR)

-   Tumour size comparison was performed determining:

    -   The percent longest diameter remaining (%DR), defined as the
        longest diameter reported in any plane post-SABR and/or at
        baseline.

    -   The percent 3D cubic volume remaining (%VR), defined as the 3D
        orthogonal cubic mm3 volume post-SABR and/or at baseline. This
        was compared against the cylindrical and spherical volumes (used
        as standard volumetric measurements by other studies/centres)

    -   Changes in BI-RADS descriptors

-   RECIST 1.1 criteria was used to evaluate response by size:

    -   MRI complete response (mCR): no sign of tumour reported

    -   MRI partial response (mPR): decrease in size $\geq 30\%$

    -   MRI no response or progression (mNR): increase in size or
        decrease in size $<30\%$

-   Lesion type descriptor changes were classified as binary change from
    mass on BL to focus, non-mass enhancement or no residual enhancement
    on the post-SABR MRI

-   Kinetic enhancement evaluation was defined as binary change to
    slower enhancement on the initial phase and binary change to less
    washout on the delayed phase:

    -   Initial Phase: change on BL to post-SABR MRI of either:

        1.  Fast to Medium or Slow

        2.  Medium to Slow

    -   Delayed Phase: change on BL to post-SABR MRI of either:

        1.  Washout to Plateau or persistent

        2.  Plateau to Persistent enhancement

-   MRI tumour dimensions were used to calculate percent cubic volume
    remaining (%VR)

-   Partial MRI response was defined as a BI-RADs descriptor change or
    %VR ≤ 70%

-   Partial pathologic response (pPR) was defined as %TC ≤ 70%

### Statistical Analysis

-   %DR and %VR on MRI were correlated with %TC using Pearson's
    correlation coefficient

-   Longest diameter on post-SABR MRI was correlated with LD on
    pathology

-   Binary changes in BI-RADS descriptors as well as mPR vs mNR were
    evaluated for use as a diagnostic test to differentiate responders
    ($\%TC \leq 70\%$) from non-responders ($\%TC > 70\%$)

-   True positives were defined as those that accurately predicted
    responders

-   True negatives were defined as those that accurately predicted
    non-responders

-   Immune response was analysed with %TILs by correlating normalised
    CelTIL scores with %DR and %VR using Pearson's correlation
    coefficient.

-   BI-RADS descriptor change were analysed by correlating %TC between
    patients with descriptor changes and patients without, using a
    two-tailed t-test (p\<0.05 were considered statistically
    significant.

### Main Results

-   Post-SABR MRI were performed a median of 38 days after SABR
    treatment (range 31-45 days)

-   Surgery was performed a median of 47 days after SABR treatment
    (range 1-21 days)

-   Changes in lesion type or enhancement kinetics was not independently
    associated with lower tumor cellularity at surgery (BI-RADS
    descriptors). However, when both were combined, a change in either
    correlated with lower %TC at surgery, compared to those with no
    change (%TC 29% vs 47%, p=0.42)

-   tumor % volume remaining on MRI post-SABR compared to baseline
    demonstrates linear correlation with pathologic % tumor cellularity

-   %TC ranged 10% to 80%

-   Cubic %VR was strongly correlative with %TC (R = 0.70, P = .0008),
    while %DR had only weak correlation (R=0.47, P = 0.04)

-   Correlation of longest diameter remaining on MRI had weak
    correlation with longest diameter at pathology, and the result was
    not statistically significant (R = 0.32, P = 0.18)

-   Cubic %VR showed slightly higher linear correlation to %TC than
    cylindric %VR (R = 0.66) and spheric %VR (R = 0.54), though
    differences were not statistically significant

-   Correlation of MRI response to CelTIL scores also showed strong
    linear correlation with %VR (R=0.72), and weak linear correlation
    with %DR

### Conclusions

-   This study shows strong linear correlations between dimension
    changes on MRI and pathologic response in patients treated with
    neoadjuvant radiation

-   This result are similar to results reported in NAC studies

-   While MRI tumor volume was not correlative to pathology size in that
    study, additional studies have demonstrated value in evaluating MRI
    tumor volume as an imaging biomarker in patients treated with NAC

-   The results of our study show that the changes detected on MRI after
    neoadjuvant radiotherapy can predict pathologic response

-   %VR evaluation showed better correlation with %TC than %DR, and has
    potential for evaluating which patients are responding the most to
    the pre-operative radiation treatment. It is suggested to include
    volumetric measurements to get a more representative assessment of
    treatment response on these patients

-   Previous studies showed differences to response in HR+ and HR-
    patients (this study considered only HER2- which is HR+). In fact,
    one of them showed longer survival rates in one group, but adverse
    effect in the other. So it is suggested to explore this method on
    both groups.

-   Similar to [@thakran_impact_2022] study, one limitation of this
    study is the small sample size.

-   Another limitation was the use of non-uniform MRI protocols, some of
    the BL MRI scans were acquired in another institution, so the
    protocols were not the same, which may have an impact on the data
    quantification. This doesn't mean a uniform protocol must be used,
    but that care must be taken to include the parameters and compensate
    potential differences when quantifying the data

### Notes

-   

## Assessment of Treatment Response with DWI and DCE-MRI in patients with early-stage breast cancer treated with sing-dose pre-op Radiotherapy [@wang_assessment_2016]

### Purpose

-   DCE-MRI and DWI MRI were used to study the treatment response
    pattern in a unique cohort of patients with early-stage breast
    cancer treated with preoperative radiation

### Population sample and procedure

-   Fifteen female qualified patients received single-dose preoperative
    radiotherapy with 1 of the 3 prescription doses: 15 Gy, 18 Gy, and
    21 Gy.

### Image acquisition and Data analysis

-   Magnetic resonance imaging scans including both diffusion-weighted
    magnetic resonance imaging and dynamic contrast-enhanced magnetic
    resonance imaging were acquired before radiotherapy for planning and
    after radiotherapy but before surgical resection

-   All MRI scans were acquired with patients in prone position on a
    1.5T GE MRI scanner using a standard 4-ch breast coil

-   Imaging protocol included T1W, T2W, DWI-MRI and DCE-MRI. The latter
    (DCE-MRI) was also used tumour delineation and radiotherapy
    planning, so they required to be of high spatial resolution with
    adequate fat-sat (but a balance was chosen between temporal and
    spatial resolution)

-   DCE-MRI:

    -   2 pre-contrast $T_1$ calibration scans (and for T1 mapping)
        using dual FA of 5 and 15deg

    -   CA gadopentetate (Magnevist) was IV administered (0.1 mmol/kg
        bw) at a rate of 2 mL/s

    -   Patients were scanned sagittally with 1 pre-contrast and 6
        post-contrast T1W fast 3D SPGR sequence (1min time resolution
        between scans)

    -   TR=6ms

    -   TE=2.9ms

    -   FOV=$24\times 24$cm

    -   Matrix size=$256\times256$

    -   Slice Thickness=3.4mm

    -   No averages

-   DWI-MRI:

    -   Sagittal plane spin-echo EPI

    -   TR=3125ms

    -   TE=77ms

    -   FOV=$30\times 30$cm

    -   Matrix size=$256\times256$

    -   Slice Thickness=5mm

    -   4 averages

    -   b-values=0 & 500mm2/s, (the latter applied in 6 directions)

-   From DWI MRI, the regional averaged ADC was calculated

-   From DCE-MRI, quantitative parameters $K^{ttrans}$ and $v_e$ were
    calculated using the standard Tofts model:

    -   Average contrast agent concentration within the ROI

    -   Semi-quantitative initial area under the concentration curve
        ($iAUC_{6min}$)

-   Relative changes of these parameters after radiotherapy were
    calculated for:

    -   GTV (Gross tumour volume)

    -   CTV (Clinical Target Volume)

    -   PTV (Planning Target Volume)

-   post-treatment scan were registered to the pre-treatment scans using
    a feature-based algorithm (quite old, from 1999) using MI as error
    metric

-   Conversion from SI to CA concentration was assumed linear and
    calculated through the T1 map, derived from the ratio between the 5
    and 15 deg pre-contrast T1W scans

### Statistical Analysis

-   

### Main Results

-   Initial results showed that after radiotherapy:

    -   iAUC significantly increased in planning target volume (P \<
        .006) and clinical target volume (P \< .006)

    -   $v_e$ significantly increased in planning target volume (P \<
        .05) and clinical target volume (P \< .05)

-   Statistical studies suggested that linear correlations between
    treatment dose and the observed parameter changes exist in most
    examined test.

-   Statistical significance was observed in:

    -   Change in GTV regional averaged ADC (P \< .012)

    -   Between treatment dose and planning target volume $K^{trans}$ (P
        \< .029)

### Conclusions

-   

### Notes

-   Apparently, registration was done between visits, but it doesn't
    mention what happened between scans (e.g. within a DCE-MRI series)

[^1]: Last updated on 06/01/2024

[^2]: user:kolab; pwd:k0lab

[^3]: An automated segmentation algorithm will be developed as part of
    the milestone #3 of this project

[^4]: Recurrence-Free-Survival

[^5]: Neoadjuvant Chemotherapy

[^6]: Note that there is an updated version of the STEEP criteria
    ([@tolaney_updated_2021]), but I believe it doesn't modify the
    criteria for RFS (but is worth checking)

[^7]: There is a typo error in the citation, it appears from 2017, but
    is from 2015

[^8]: there is an update method called N4ITKs [@tustison_n4itk_2010]
    which may be worth considering

[^9]: It is used to improve image registration, but. still need to
    understand how it is done!!

[^10]: Local Binary Patterns, see [LBP histogram for rotation invariant
    texture
    classification.](https://ieeexplore.ieee.org/document/1017623)

[^11]: Neoadjuvant Partial Breast Irradiation

[^12]: Stereotactic Ablative Body Radiotherapy

[^13]: Tumour Cellularity

[^14]: Percent Tumour Infiltrating Lymphocytes

[^15]: [Breast Imaging Reporting & Data
    System](https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems/Bi-Rads)
