import pytorch_lightning as pl
from models.feedback import argparser
from models.feedback.model import Model
from models.feedback.data_module import DataModule
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelCheckpoint
from models.feedback.config import GPUS,ACCELERATOR
from copy import deepcopy

args = argparser.get_args()

if __name__ == "__main__":
    
    trainer = pl.Trainer(
        gpus=GPUS,
        accelerator=ACCELERATOR,
        fast_dev_run=args.dev,
        precision=32,
        default_root_dir='.log_feedback',
        max_epochs=args.epoch,
        callbacks=[
            # EarlyStopping(monitor='dev_loss',patience=3),
            # ModelCheckpoint(monitor='dev_loss',filename='{epoch}-{dev_loss:.2f}',save_last=True),
            ModelCheckpoint(save_last=True),
        ]
    )

    # DataModule
    dm = DataModule()

    # from_checkpoint
    if args.from_checkpoint is None:
        model = Model()
    else:
        print('load from checkpoint')
        model = Model.load_from_checkpoint(args.from_checkpoint)
    
    # train
    if args.run_test == False:
        # tuner = pl.tuner.tuning.Tuner(deepcopy(trainer))
        # new_batch_size = tuner.scale_batch_size(model, datamodule=dm)
        # model.hparams.batch_size = new_batch_size
        trainer.fit(model,datamodule=dm)

    # run_test
    last_model_path = trainer.checkpoint_callback.last_model_path
    best_model_path = trainer.checkpoint_callback.best_model_path
    _use_model_path = last_model_path if best_model_path == "" else best_model_path
    print('use checkpoint:',_use_model_path)
    trainer.test(
            model=model if _use_model_path == "" else None,
            datamodule=dm,
            ckpt_path=_use_model_path
        )