from run.rule_engine import RuleEngine

from .input_processing_rules import \
    SetupExtractionRule,\
    RequestExtractionRule

from .language_model_prediction_rules import \
    ReferringExpressionPredictionRule,\
    DialogueActPredictionRule

from .established_reference_rules import \
    VisualizationSpecificationCreationRule

from .discourse_rules import \
    DiscourseTypeRule

from .create_vis_not_from_existing_template_discourse_rules import \
    VisualizationSpecificationStateUpdateRule as VisualizationSpecificationStateUpdateNotFromTemplateRule

from ..shared_create_vis_not_from_existing_template_discourse_rules import \
    VisualizationSpecificationDialogueHistoryAdditionRule as \
        VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateRule

from .create_vis_from_existing_template_discourse_rules import \
    SearchPreviousVisualizationSpecificationUsingGestureReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingGestureReferenceFromTemplateRule, \
    SearchPreviousVisualizationSpecificationUsingTextReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingTextReferenceFromTemplateRule, \
    VisualizationSpecificationStateUpdateRule as VisualizationSpecificationStateUpdateFromTemplateRule

from ..shared_create_vis_from_existing_template_discourse_rules import \
    MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule as \
        MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromTemplateRule, \
    VisualizationSpecificationDialogueHistoryAdditionRule as \
        VisualizationSpecificationDialogueHistoryAdditionFromTemplateRule

from .existing_vis_discourse_rules import \
    SearchPreviousVisualizationSpecificationUsingGestureReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingGestureReferenceFromExistingVisRule, \
    SearchPreviousVisualizationSpecificationUsingTextReferenceRule as \
        SearchPreviousVisualizationSpecificationUsingTextReferenceFromExistingVisRule, \
    MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule as \
        MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromExistingVisRule


class RuleEngineFactory:
    @staticmethod
    def build():
        input_processing_rules_engine = RuleEngine()
        input_processing_rules_engine\
            .register_rule(SetupExtractionRule())\
            .register_rule(RequestExtractionRule())

        language_model_prediction_rules_engine = RuleEngine()
        language_model_prediction_rules_engine \
            .register_rule(ReferringExpressionPredictionRule()) \
            .register_rule(DialogueActPredictionRule())

        established_reference_rules_engine = RuleEngine()
        established_reference_rules_engine\
            .register_rule(VisualizationSpecificationCreationRule())

        discourse_rules_engine = RuleEngine()
        discourse_rules_engine\
            .register_rule(DiscourseTypeRule())

        create_vis_not_from_existing_template_discourse_rules_engine = RuleEngine()
        create_vis_not_from_existing_template_discourse_rules_engine\
            .register_rule(VisualizationSpecificationStateUpdateNotFromTemplateRule())\
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionNotFromTemplateRule())

        create_vis_from_existing_template_discourse_rules_engine = RuleEngine()
        create_vis_from_existing_template_discourse_rules_engine\
            .register_rule(SearchPreviousVisualizationSpecificationUsingGestureReferenceFromTemplateRule())\
            .register_rule(SearchPreviousVisualizationSpecificationUsingTextReferenceFromTemplateRule()) \
            .register_rule(
                MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromTemplateRule()) \
            .register_rule(VisualizationSpecificationStateUpdateFromTemplateRule())\
            .register_rule(VisualizationSpecificationDialogueHistoryAdditionFromTemplateRule())

        existing_vis_discourse_rules_engine = RuleEngine()
        existing_vis_discourse_rules_engine\
            .register_rule(SearchPreviousVisualizationSpecificationUsingGestureReferenceFromExistingVisRule())\
            .register_rule(SearchPreviousVisualizationSpecificationUsingTextReferenceFromExistingVisRule())\
            .register_rule(
                MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationFromExistingVisRule())

        return input_processing_rules_engine, \
               language_model_prediction_rules_engine, \
               established_reference_rules_engine, \
               discourse_rules_engine, \
               create_vis_not_from_existing_template_discourse_rules_engine, \
               create_vis_from_existing_template_discourse_rules_engine, \
               existing_vis_discourse_rules_engine
