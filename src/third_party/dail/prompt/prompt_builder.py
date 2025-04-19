from src.third_party.dail.dail_conf import DailParams
from src.third_party.dail.utils.enums import REPR_TYPE
from src.third_party.dail.utils.enums import EXAMPLE_TYPE
from src.third_party.dail.utils.enums import SELECTOR_TYPE
from src.third_party.dail.prompt.PromptReprTemplate import *
from src.third_party.dail.prompt.ExampleFormatTemplate import *
from src.third_party.dail.prompt.ExampleSelectorTemplate import *
from src.third_party.dail.prompt.PromptICLTemplate import BasicICLPrompt
from src.util.log_util import log


def get_repr_cls(repr_type: str):
    if repr_type == REPR_TYPE.CODE_REPRESENTATION:
        repr_cls = SQLPrompt
    elif repr_type == REPR_TYPE.TEXT_REPRESENTATION:
        repr_cls = TextPrompt
    elif repr_type == REPR_TYPE.OPENAI_DEMOSTRATION:
        repr_cls = NumberSignPrompt
    elif repr_type == REPR_TYPE.BASIC:
        repr_cls = BaselinePrompt
    elif repr_type == REPR_TYPE.ALPACA_SFT:
        repr_cls = InstructionPrompt
    elif repr_type == REPR_TYPE.OPENAI_DEMOSTRATION_WFK:
        repr_cls = NumberSignWithForeignKeyPrompt
    elif repr_type == REPR_TYPE.BASIC_WOFK:
        repr_cls = BaselineWithoutForeignKeyPrompt
    elif repr_type == REPR_TYPE.TEXT_REPRESENTATION_WFK:
        repr_cls = TextWithForeignKeyPrompt
    elif repr_type == REPR_TYPE.ALPACA_SFT_WFK:
        repr_cls = InstructionWithForeignKeyPrompt
    elif repr_type == REPR_TYPE.OPENAI_DEMOSTRATION_WORULE:
        repr_cls = NumberSignWithoutRulePrompt
    elif repr_type == REPR_TYPE.CODE_REPRESENTATION_WRULE:
        repr_cls = SQLWithRulePrompt
    elif repr_type == REPR_TYPE.ALPACA_SFT_WRULE:
        repr_cls = InstructionWithRulePrompt
    elif repr_type == REPR_TYPE.TEXT_REPRESENTATION_WRULE:
        repr_cls = TextWithRulePrompt
    elif repr_type == REPR_TYPE.CODE_REPRESENTATION_COT:
        repr_cls = SQLCOTPrompt
    elif repr_type == REPR_TYPE.TEXT_REPRESENTATION_COT:
        repr_cls = TextCOTPrompt
    elif repr_type == REPR_TYPE.OPENAI_DEMOSTRATION_COT:
        repr_cls = NumberSignCOTPrompt
    elif repr_type == REPR_TYPE.ALPACA_SFT_COT:
        repr_cls = InstructionCOTPrompt
    elif repr_type == REPR_TYPE.CBR:
        repr_cls = CBRPrompt
    else:
        raise ValueError(f"{repr_type} is not supproted yet")
    return repr_cls


def get_example_format_cls(example_format: str):
    if example_format == EXAMPLE_TYPE.ONLY_SQL:
        example_format_cls = SqlExampleStyle
    elif example_format == EXAMPLE_TYPE.QA:
        example_format_cls = QuestionSqlExampleStyle
    elif example_format == EXAMPLE_TYPE.QAWRULE:
        example_format_cls = QuestionSqlWithRuleExampleStyle
    elif example_format == EXAMPLE_TYPE.COMPLETE:
        example_format_cls = CompleteExampleStyle
    elif example_format == EXAMPLE_TYPE.OPENAI_DEMOSTRATION_QA:
        example_format_cls = NumberSignQuestionSqlExampleStyle
    elif example_format == EXAMPLE_TYPE.BASIC_QA:
        example_format_cls = BaselineQuestionSqlExampleStyle
    else:
        raise ValueError(f"{example_format} is not supported yet!")
    return example_format_cls


def get_example_selector(selector_type: str):
    if selector_type == SELECTOR_TYPE.COS_SIMILAR:
        selector_cls = CosineSimilarExampleSelector
    elif selector_type == SELECTOR_TYPE.RANDOM:
        selector_cls = RandomExampleSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE:
        selector_cls = EuclideanDistanceExampleSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_THRESHOLD:
        selector_cls = EuclideanDistanceThresholdExampleSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_SKELETON_SIMILARITY_THRESHOLD:
        selector_cls = EuclideanDistanceSkeletonSimilarThresholdSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_QUESTION_MASK:
        selector_cls = EuclideanDistanceQuestionMaskSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_PRE_SKELETON_SIMILARITY_THRESHOLD:
        selector_cls = EuclideanDistancePreSkeletonSimilarThresholdSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_PRE_SKELETON_SIMILARITY_PLUS:
        selector_cls = EuclideanDistancePreSkeletonSimilarPlusSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_MASK_PRE_SKELETON_SIMILARITY_THRESHOLD:
        selector_cls = EuclideanDistanceQuestionMaskPreSkeletonSimilarThresholdSelector
    elif selector_type == SELECTOR_TYPE.EUC_DISTANCE_MASK_PRE_SKELETON_SIMILARITY_THRESHOLD_SHIFT:
        selector_cls = EuclideanDistanceQuestionMaskPreSkeletonSimilarThresholdShiftSelector
    else:
        raise ValueError(f"{selector_type} is not supported yet!")
    return selector_cls


@log("Dail prompt creation")
def prompt_factory(params: DailParams, data, second_stage: bool):
    tokenizer = params.tokenizer
    repr_type = params.prompt_repr
    k_shot = params.k_shot
    example_format = params.example_type

    if not second_stage:
        selector_type = params.selector_type
    else:
        selector_type = params.second_selector_type

    repr_cls = get_repr_cls(repr_type)

    if k_shot == 0:
        assert repr_cls is not None
        cls_name = f"{repr_type}_{k_shot}-SHOT"

        target_formatter = repr_cls()
        return BasicICLPrompt(name=cls_name, num_examples=k_shot, tokenizer=tokenizer,
                              target_formatter=target_formatter)
    else:
        example_format_cls = get_example_format_cls(example_format)
        selector_cls = get_example_selector(selector_type)
        cls_name = f"{repr_type}_{k_shot}-SHOT_{selector_type}_{example_format}-EXAMPLE"

        target_formatter = repr_cls()
        example_selector = selector_cls(data)
        example_format_template = example_format_cls()

        return BasicICLPrompt(name=cls_name, num_examples=k_shot, tokenizer=tokenizer,
                              target_formatter=target_formatter, example_selector=example_selector,
                              example_format_template=example_format_template)
