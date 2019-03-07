# pylint: skip-file
import tensorflow as tf
from open_seq2seq.models import Speech2Text
from open_seq2seq.encoders import TSSEncoder
from open_seq2seq.decoders import FullyConnectedCTCDecoder
from open_seq2seq.data.speech2text.speech2text import Speech2TextDataLayer
from open_seq2seq.losses import CTCLoss
from open_seq2seq.optimizers.lr_policies import transformer_policy

base_model = Speech2Text
data_root = '/data/librispeech/'
d_model = 1024

base_params = {
    "random_seed": 0,
    "use_horovod": True,
    "num_epochs": 50,

    "num_gpus": 1,
    "batch_size_per_gpu": 32,
    "iter_size": 1,

    "save_summaries_steps": 100,
    "print_loss_steps": 10,
    "print_samples_steps": 2200,
    "eval_steps": 2200,
    "save_checkpoint_steps": 1100,
    "num_checkpoints": 5,
    "logdir": "yasper_log_folder",

    # "optimizer": "Momentum",
    # "optimizer_params": {
    #     "momentum": 0.90,
    # },
    # "lr_policy": poly_decay,
    # "lr_policy_params": {
    #     "learning_rate": 0.01,
    #     "min_lr": 1e-5,
    #     "power": 2.0,
    # },
    # "larc_params": {
    #     "larc_eta": 0.001,
    # },

    "optimizer": tf.contrib.opt.LazyAdamOptimizer,
    "optimizer_params": {
        "beta1": 0.9,
        "beta2": 0.997,
        "epsilon": 1e-09,
    },

    "lr_policy": transformer_policy,
    "lr_policy_params": {
        "learning_rate": 2.0,
        "warmup_steps": 2000,
        "d_model": d_model,
    },

    "regularizer": tf.contrib.layers.l2_regularizer,
    "regularizer_params": {
        'scale': 0.001
    },

    "dtype": "mixed",
    "loss_scaling": "Backoff",

    "summaries": ['learning_rate', 'variables', 'gradients', 'larc_summaries',
                  'variable_norm', 'gradient_norm', 'global_gradient_norm'],

    "encoder": TSSEncoder,
    "encoder_params": {
        "convnet_layers": [
            {
                "type": "conv1d", "repeat": 1,
                "kernel_size": [11], "stride": [2],
                "num_channels": 128, "padding": "SAME",
                "dilation":[1], "dropout_keep_prob": 0.8,
            },
            {
                "type": "conv1d", "repeat": 1,
                "kernel_size": [1], "stride": [1],
                "num_channels": d_model, "padding": "SAME",
                "dilation": [1], "dropout_keep_prob": 0.8,
            },

        ],
        "dropout_keep_prob": 0.7,
        "initializer": tf.contrib.layers.xavier_initializer,
        "initializer_params": {
            'uniform': False,
        },
        "normalization": "batch_norm",
        "activation_fn": lambda x: tf.minimum(tf.nn.relu(x), 20.0),
        "data_format": "channels_last",

        "encoder_layers": [(32, 32)]*8,
        "hidden_size": d_model,
        "num_heads": 16,
        "attention_dropout": 0.4,
        "filter_size": 4 * d_model,
        "relu_dropout": 0.4,
        "layer_postprocess_dropout": 0.4,
    },

    "decoder": FullyConnectedCTCDecoder,
    "decoder_params": {
        "initializer": tf.contrib.layers.xavier_initializer,
        "use_language_model": False,

        # params for decoding the sequence with language model
        "beam_width": 512,
        "alpha": 2.0,
        "beta": 1.5,

        "decoder_library_path": "ctc_decoder_with_lm/libctc_decoder_with_kenlm.so",
        "lm_path": "language_model/4-gram.binary",
        "trie_path": "language_model/trie.binary",
        "alphabet_config_path": "open_seq2seq/test_utils/toy_speech_data/vocab.txt",
    },
    "loss": CTCLoss,
    "loss_params": {},
}

train_params = {
    "data_layer": Speech2TextDataLayer,
    "data_layer_params": {
        "num_audio_features": 64,
        "input_type": "logfbank",
        "vocab_file": "open_seq2seq/test_utils/toy_speech_data/vocab.txt",
        "dataset_files": [
            data_root + "librivox-train-clean-100.csv",
            data_root + "librivox-train-clean-360.csv",
            data_root + "librivox-train-other-500.csv",
        ],

        "max_duration": 16.7,
        "shuffle": True,
    },
}

eval_params = {
    "data_layer": Speech2TextDataLayer,
    "data_layer_params": {
        "num_audio_features": 64,
        "input_type": "logfbank",
        "vocab_file": "open_seq2seq/test_utils/toy_speech_data/vocab.txt",
        "dataset_files": [
            data_root + "librivox-dev-clean.csv",
        ],
        "shuffle": False,
    },
}

infer_params = {
    "data_layer": Speech2TextDataLayer,
    "data_layer_params": {
        "num_audio_features": 64,
        "input_type": "logfbank",
        "vocab_file": "open_seq2seq/test_utils/toy_speech_data/vocab.txt",
        "dataset_files": [
            data_root + "librivox-test-clean.csv",
        ],
        "shuffle": False,
    },
}
