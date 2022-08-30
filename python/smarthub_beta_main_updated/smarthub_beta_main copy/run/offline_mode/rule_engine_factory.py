from run.rule_engine import RuleEngine

from .input_processing_rules import \
    ContextComponentExtractionRule, \
    SetupExtractionRule, \
    RequestExtractionRule, \
    GestureExtractionRule, \
    TextExtractionRule

from .language_model_prediction_rules import \
    ReferringExpressionPredictionRule, \
    DialogueActPredictionRule, \
    DialogueActExtractionRule, \
    DialogueActStatisticsRule

from .established_reference_rules import \
    VisualizationSpecificationCreationRule

from .discourse_rules import \
    DiscourseTypeRule

from .create_vis_not_from_existing_template_discourse_rules import \
    VisualizationSpecificationStateUpdateRule as VisualizationSpecificationStateUpdateNotFromTemplateRule, \
    ExtractVisualizationSpecificationPropertiesRule as ExtractVisualizationSpecificationPropertiesNotFromTemplateRule, \
    VisualizationSpecificationDialogueHistoryAdditionStatisticsRule as \
        VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateStatisticsRule, \
    VisualizationSpecificationDialogueHistoryAdditionPlotTypeStatisticsRule as \
        VisualizationSpecificationDialogueHistoryAdditionPlotTypeNotFromTemplateStatisticsRule, \
    VisualizationSpecificationPropertiesStatisticsRule as \
        VisualizationSpecificationPropertiesNotFromTemplateStatisticsRule

from ..shared_create_vis_not_from_existing_template_discourse_rules import \
    VisualizationSpecificationDialogueHistoryAdditionRule as \
        VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateRule, \
    PredictVisualizationSpecificationPropertiesRule as PredictVisualizationSpecificationPropertiesNotFromTemplateRule

from .create_vis_from_existing_template_discourse_rules import \
    ExtractDistanceToPreviousVisualizationUsingGestureReferenceRule as \
        ExtractDistanceToPreviousVisualizationUsingGestureReferenceFromTemplateRule, \
    SearchPreviousVisualizationSpecificationUsingGestureReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingGestureReferenceFromTemplateRule, \
    GestureTargetIdStatisticsRule as GestureTargetIdFromTemplateStatisticsRule, \
    GestureTargetIdDistanceStatisticsRule as GestureTargetIdDistanceFromTemplateStatisticsRule, \
    GestureReferringExpressionStatisticsRule as GestureReferringExpressionFromTemplateStatisticsRule, \
    ExtractDistanceToPreviousVisualizationUsingTextReferenceRule as \
        ExtractDistanceToPreviousVisualizationUsingTextReferenceFromTemplateRule, \
    SearchPreviousVisualizationSpecificationUsingTextReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingTextReferenceFromTemplateRule, \
    TextTargetIdStatisticsRule as TextTargetIdFromTemplateStatisticsRule, \
    TextTargetIdDistanceStatisticsRule as TextTargetIdDistanceFromTemplateStatisticsRule, \
    TextReferringExpressionStatisticsRule as TextReferringExpressionFromTemplateStatisticsRule, \
    VisualizationSpecificationStateUpdateRule as VisualizationSpecificationStateUpdateFromTemplateRule, \
    ExtractVisualizationSpecificationPropertiesRule as ExtractVisualizationSpecificationPropertiesFromTemplateRule, \
    VisualizationSpecificationPropertiesStatisticsRule as VisualizationSpecificationPropertiesFromTemplateStatisticsRule, \
    VisualizationSpecificationDialogueHistoryAdditionStatisticsRule as \
        VisualizationSpecificationDialogueHistoryAdditionFromTemplateStatisticsRule, \
    VisualizationSpecificationDialogueHistoryAdditionPlotTypeStatisticsRule as \
        VisualizationSpecificationDialogueHistoryAdditionPlotTypeFromTemplateStatisticsRule

from ..shared_create_vis_from_existing_template_discourse_rules import \
    MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule as \
        MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromTemplateRule, \
    VisualizationSpecificationDialogueHistoryAdditionRule as \
        VisualizationSpecificationDialogueHistoryAdditionFromTemplateRule, \
    PredictVisualizationSpecificationPropertiesRule as PredictVisualizationSpecificationPropertiesFromTemplateRule

from .existing_vis_discourse_rules import \
    ExtractDistanceToPreviousVisualizationUsingGestureReferenceRule as \
        ExtractDistanceToPreviousVisualizationUsingGestureReferenceFromExistingVisRule, \
    SearchPreviousVisualizationSpecificationUsingGestureReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingGestureReferenceFromExistingVisRule, \
    GestureTargetIdStatisticsRule as GestureTargetIdFromExistingVisStatisticsRule, \
    GestureTargetIdDistanceStatisticsRule as GestureTargetIdDistanceFromExistingVisStatisticsRule, \
    GestureReferringExpressionStatisticsRule as GestureReferringExpressionFromExistingVisStatisticsRule, \
    ExtractDistanceToPreviousVisualizationUsingTextReferenceRule as \
        ExtractDistanceToPreviousVisualizationUsingTextReferenceFromExistingVisRule, \
    SearchPreviousVisualizationSpecificationUsingTextReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingTextReferenceFromExistingVisRule, \
    TextTargetIdStatisticsRule as TextTargetIdFromExistingVisStatisticsRule, \
    TextTargetIdDistanceStatisticsRule as TextTargetIdDistanceFromExistingVisStatisticsRule, \
    TextReferringExpressionStatisticsRule as TextReferringExpressionFromExistingVisStatisticsRule, \
    MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule as \
        MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromExistingVisRule


class RuleEngineFactory:
    @staticmethod
    def build():
        input_processing_rules_engine = RuleEngine()
        input_processing_rules_engine \
            .register_rule(ContextComponentExtractionRule()) \
            .register_rule(SetupExtractionRule()) \
            .register_rule(RequestExtractionRule()) \
            .register_rule(TextExtractionRule()) \
            .register_rule(GestureExtractionRule())

        language_model_prediction_rules_engine = RuleEngine()
        language_model_prediction_rules_engine \
            .register_rule(ReferringExpressionPredictionRule()) \
            .register_rule(DialogueActPredictionRule()) \
            .register_rule(DialogueActExtractionRule()) \
            .register_rule(DialogueActStatisticsRule())

        established_reference_rules_engine = RuleEngine()
        established_reference_rules_engine \
            .register_rule(VisualizationSpecificationCreationRule())

        discourse_rules_engine = RuleEngine()
        discourse_rules_engine \
            .register_rule(DiscourseTypeRule())

        create_vis_not_from_existing_template_discourse_rules_engine = RuleEngine()
        create_vis_not_from_existing_template_discourse_rules_engine \
            .register_rule(VisualizationSpecificationStateUpdateNotFromTemplateRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateStatisticsRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionPlotTypeNotFromTemplateStatisticsRule()) \
            .register_rule(ExtractVisualizationSpecificationPropertiesNotFromTemplateRule()) \
            .register_rule(PredictVisualizationSpecificationPropertiesNotFromTemplateRule()) \
            .register_rule(VisualizationSpecificationPropertiesNotFromTemplateStatisticsRule())

        create_vis_from_existing_template_discourse_rules_engine = RuleEngine()
        create_vis_from_existing_template_discourse_rules_engine \
            .register_rule(ExtractDistanceToPreviousVisualizationUsingGestureReferenceFromTemplateRule()) \
            .register_rule(SearchPreviousVisualizationSpecificationUsingGestureReferenceFromTemplateRule()) \
            .register_rule(GestureTargetIdFromTemplateStatisticsRule()) \
            .register_rule(GestureTargetIdDistanceFromTemplateStatisticsRule()) \
            .register_rule(GestureReferringExpressionFromTemplateStatisticsRule()) \
            .register_rule(ExtractDistanceToPreviousVisualizationUsingTextReferenceFromTemplateRule()) \
            .register_rule(SearchPreviousVisualizationSpecificationUsingTextReferenceFromTemplateRule()) \
            .register_rule(TextTargetIdFromTemplateStatisticsRule()) \
            .register_rule(TextTargetIdDistanceFromTemplateStatisticsRule()) \
            .register_rule(TextReferringExpressionFromTemplateStatisticsRule()) \
            .register_rule(
                MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromTemplateRule()) \
            .register_rule(VisualizationSpecificationStateUpdateFromTemplateRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionFromTemplateRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionFromTemplateStatisticsRule()) \
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionPlotTypeFromTemplateStatisticsRule()) \
            .register_rule(ExtractVisualizationSpecificationPropertiesFromTemplateRule()) \
            .register_rule(PredictVisualizationSpecificationPropertiesFromTemplateRule()) \
            .register_rule(VisualizationSpecificationPropertiesFromTemplateStatisticsRule())

        existing_vis_discourse_rules_engine = RuleEngine()
        existing_vis_discourse_rules_engine \
            .register_rule(ExtractDistanceToPreviousVisualizationUsingGestureReferenceFromExistingVisRule()) \
            .register_rule(SearchPreviousVisualizationSpecificationUsingGestureReferenceFromExistingVisRule()) \
            .register_rule(GestureTargetIdFromExistingVisStatisticsRule()) \
            .register_rule(GestureTargetIdDistanceFromExistingVisStatisticsRule()) \
            .register_rule(GestureReferringExpressionFromExistingVisStatisticsRule()) \
            .register_rule(ExtractDistanceToPreviousVisualizationUsingTextReferenceFromExistingVisRule()) \
            .register_rule(SearchPreviousVisualizationSpecificationUsingTextReferenceFromExistingVisRule()) \
            .register_rule(TextTargetIdFromExistingVisStatisticsRule()) \
            .register_rule(TextTargetIdDistanceFromExistingVisStatisticsRule()) \
            .register_rule(TextReferringExpressionFromExistingVisStatisticsRule()) \
            .register_rule(
                MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromExistingVisRule())

        return input_processing_rules_engine, \
               language_model_prediction_rules_engine, \
               established_reference_rules_engine, \
               discourse_rules_engine, \
               create_vis_not_from_existing_template_discourse_rules_engine, \
               create_vis_from_existing_template_discourse_rules_engine, \
               existing_vis_discourse_rules_engine
