from easyvolcap.utils.console_utils import *
from easyvolcap.engine import DATASETS

import torch
from torch.utils.data import Dataset
from easyvolcap.dataloaders.datasets.volumetric_video_dataset import VolumetricVideoDataset


@DATASETS.register_module()
class NoopDataset(Dataset):
    def __init__(self, frame_sample, view_sample, closest_using_t=False, near=0.02, far=20, bounds=torch.as_tensor([[-5, -5, -5], [5, 5, 5]]), render_ratio=1.0, **kwargs):
        self.view_sample = view_sample
        self.frame_sample = frame_sample
        self.closest_using_t = closest_using_t
        self.n_views = (view_sample[1] - view_sample[0]) // view_sample[2]
        self.n_latents = (frame_sample[1] - frame_sample[0]) // frame_sample[2]
        self.n_frame_total = self.n_latents
        self.n_view_total = self.n_views

        self.Rv = torch.as_tensor([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0],
        ])  # 3, 3
        self.Tv = torch.as_tensor([0, 0, 3])  # 3, 1
        self.near = near
        self.far = far
        self.bounds = torch.as_tensor(bounds)
        self.render_ratio = render_ratio

    def __len__(self):
        return self.n_latents * self.n_views

    @property
    def frame_min(self): return VolumetricVideoDataset.frame_min.fget(self)
    @property
    def frame_max(self): return VolumetricVideoDataset.frame_max.fget(self)
    @property
    def frame_int(self): return VolumetricVideoDataset.frame_int.fget(self)
    @property
    def frame_range(self): return VolumetricVideoDataset.frame_range.fget(self)

    @property
    def view_min(self): return VolumetricVideoDataset.view_min.fget(self)
    @property
    def view_max(self): return VolumetricVideoDataset.view_max.fget(self)
    @property
    def view_int(self): return VolumetricVideoDataset.view_int.fget(self)
    @property
    def view_range(self): return VolumetricVideoDataset.view_range.fget(self)

    def t_to_frame(self, t): return VolumetricVideoDataset.t_to_frame(self, t)

    def frame_to_t(self, frame_index): return VolumetricVideoDataset.frame_to_t(self, frame_index)

    def frame_to_latent(self, frame_index): return VolumetricVideoDataset.frame_to_latent(self, frame_index)

    def camera_to_v(self, camera_index): return VolumetricVideoDataset.camera_to_v(self, camera_index)

    def v_to_camera(self, v): return VolumetricVideoDataset.v_to_camera(self, v)

    def camera_to_view(self, camera_index): return VolumetricVideoDataset.camera_to_view(self, camera_index)

    def get_bounds(self, latent_index): return VolumetricVideoDataset.get_bounds(self, latent_index)

    def virtual_to_physical(self, latent_index): return latent_index

    def physical_to_virtual(self, latent_index): return latent_index

    def get_viewer_batch(self, output: dotdict):
        # Source indices
        t = output.t
        v = output.v
        bounds = output.bounds  # camera bounds
        frame_index = self.t_to_frame(t)
        camera_index = self.v_to_camera(v)
        latent_index = self.frame_to_latent(frame_index)
        view_index = self.camera_to_view(camera_index)

        # Update indices, maybe not needed
        output.view_index = view_index
        output.frame_index = frame_index
        output.camera_index = camera_index
        output.latent_index = latent_index
        output.meta.view_index = view_index
        output.meta.frame_index = frame_index
        output.meta.camera_index = camera_index
        output.meta.latent_index = latent_index

        output.bounds = self.get_bounds(latent_index)  # will crop according to batch bounds
        output.bounds[0] = torch.maximum(output.bounds[0], bounds[0])  # crop according to user bound
        output.bounds[1] = torch.minimum(output.bounds[1], bounds[1])
        output.meta.bounds = output.bounds
        return output
