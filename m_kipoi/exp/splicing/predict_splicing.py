import kipoi
import kipoi.postprocessing.variant_effects.snv_predict as sp
from kipoi.postprocessing.variant_effects import Diff, Logit, VcfWriter, ensure_tabixed_vcf
from kipoi.cli.postproc import _get_scoring_fns
import json

model_df = None


def get_model_df():
    global model_df
    if model_df is None:
        model_df = kipoi.list_models()
    return model_df


def get_all_models(substr, install_reqs=False):
    # Run effect predicton
    models_df = get_model_df()
    models_substr = [substr]
    models_df_subsets = {ms: models_df.loc[models_df["model"].str.contains(ms)] for ms in models_substr}
    #
    if install_reqs:
        for ms in models_substr:
            model_name = models_df_subsets[ms]["model"].iloc[0]
            kipoi.pipeline.install_model_requirements(model_name)
    return models_df_subsets


def _output_vcf_path(output_vcf_expr, model_name):
    return output_vcf_expr % model_name.replace("/", "_")


def to_output_vcfs(substr, output_vcf_expr):
    outputs = []
    models_df_subsets = get_all_models(substr)
    for k in models_df_subsets:
        outputs.extend([_output_vcf_path(output_vcf_expr, model_name)] for model_name in models_df_subsets[k]["model"])
    return outputs


def predict_model_auto(models_substr, gtf_file, fasta_file, input_vcf, output_vcf_expr):
    """
    Arguments: 
    - models_substr: model substring e.g. 'HAL'
    - gtf_file: 
    - fasta_file: 
    - input_vcf: 
    - output_vcf_expr:
    """
    assert models_substr in ["HAL", "MaxEntScan", "labranchor"]
    models_df_subsets = get_all_models(models_substr, True)
    dataloader_arguments = {"gtf_file": gtf_file, "fasta_file": fasta_file}
    for ms in models_df_subsets:
        for model_name in models_df_subsets[ms]["model"]:
            model = kipoi.get_model(model_name)
            vcf_path_tbx = ensure_tabixed_vcf(input_vcf)
            out_vcf_fpath = _output_vcf_path(output_vcf_expr, model_name)
            writer = VcfWriter(model, input_vcf, out_vcf_fpath)
            Dataloader = kipoi.get_dataloader_factory(model_name)
            vcf_to_region = None
            sp.predict_snvs(model,
                            Dataloader,
                            vcf_path_tbx,
                            batch_size=32,
                            dataloader_args=dataloader_arguments,
                            vcf_to_region=vcf_to_region,
                            evaluation_function_kwargs={'diff_types': {'diff': Diff("mean")}},
                            sync_pred_writer=writer)


def predict_model(model_name, gtf_file, fasta_file, input_vcf, out_vcf_fpath, batch_size=32, num_workers=0):
    dataloader_arguments = {"gtf_file": gtf_file, "fasta_file": fasta_file}
    model = kipoi.get_model(model_name)
    vcf_path_tbx = ensure_tabixed_vcf(input_vcf)
    writer = VcfWriter(model, input_vcf, out_vcf_fpath)
    Dataloader = kipoi.get_dataloader_factory(model_name)
    vcf_to_region = None
    default_params = {"rc_merging": "absmax"}
    scr_labels = ["logit_ref", "logit_alt", "ref", "alt", "logit", "diff"]
    scr_config = [default_params] * len(scr_labels)
    difftypes = _get_scoring_fns(model, scr_labels, [json.dumps(el) for el in scr_config])
    sp.predict_snvs(model,
                    Dataloader,
                    vcf_path_tbx,
                    batch_size=batch_size,
                    dataloader_args=dataloader_arguments,
                    num_workers=num_workers,
                    vcf_to_region=vcf_to_region,
                    evaluation_function_kwargs={'diff_types': difftypes},
                    sync_pred_writer=writer)


# TODO - is this already part of the original library?

def score_variants(model,
                   dl_args,
                   input_vcf,
                   output_vcf,
                   scores=["logit_ref", "logit_alt", "ref", "alt", "logit", "diff"],
                   num_workers=0,
                   batch_size=32,
                   dataloader=None,
                   source='kipoi'):
    """Score variants: annotate the vcf file using
    model predictions for the refernece and alternative alleles
    Args:
      model: model string or a model class instance
      dl_args: dataloader arguments as a dictionary
      input_vcf: input vcf file path
      output_vcf: output vcf file path
      scores: list of score names to compute. See kipoi.postprocessing.variant_effects.utils.scoring_fns
      num_workers: number of paralell workers to use for dataloadeing
      batch_size: batch_size for dataloading
      source: model source name
    """
    if isinstance(model, str):
        if dataloader is None:
            model = kipoi.get_model(model, source=source, with_dataloader=True)
            Dataloader = model.default_dataloader
        else:
            model = kipoi.get_model(model, source=source, with_dataloader=False)
            if isinstance(dataloader, str):
                Dataloader = kipoi.get_dataloader_factory(dataloader, source=source)
            else:
                Dataloader = dataloader
    vcf_path_tbx = ensure_tabixed_vcf(input_vcf)  # TODO - run this within the function
    writer = VcfWriter(model, input_vcf, output_vcf)
    vcf_to_region = None
    default_params = {"rc_merging": "absmax"}
    scr_config = [default_params] * len(scores)
    difftypes = _get_scoring_fns(model, scores, [json.dumps(el) for el in scr_config])
    # ----
    sp.predict_snvs(model,
                    Dataloader,
                    vcf_path_tbx,
                    batch_size=batch_size,
                    dataloader_args=dl_args,
                    num_workers=num_workers,
                    vcf_to_region=vcf_to_region,
                    evaluation_function_kwargs={'diff_types': difftypes},
                    sync_pred_writer=writer)
