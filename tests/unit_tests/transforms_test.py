import unittest

import numpy as np

from super_gradients.training.transforms.keypoint_transforms import (
    KeypointsRandomHorizontalFlip,
    KeypointsRandomVerticalFlip,
    KeypointsRandomAffineTransform,
    KeypointsPadIfNeeded,
    KeypointsLongestMaxSize,
)


class TestTransforms(unittest.TestCase):
    def test_keypoints_random_affine(self):
        image = np.random.rand(640, 480, 3)
        mask = np.random.rand(640, 480)
        joints = np.random.randint(0, 480, size=(1, 17, 3))
        joints[..., 2] = 2  # all visible

        aug = KeypointsRandomAffineTransform(min_scale=0.8, max_scale=1.2, max_rotation=30, max_translate=0.5, prob=1, image_pad_value=0, mask_pad_value=0)
        aug_image, aug_mask, aug_joints = aug(image, mask, joints)

        joints_outside_image = (
            (aug_joints[:, :, 0] < 0) | (aug_joints[:, :, 1] < 0) | (aug_joints[:, :, 0] >= aug_image.shape[1]) | (aug_joints[:, :, 1] >= aug_image.shape[0])
        )
        # Ensure that keypoints outside the image are not visible
        self.assertTrue((aug_joints[joints_outside_image, 2] == 0).all())
        self.assertTrue((aug_joints[~joints_outside_image, 2] != 0).all())

    def test_keypoints_horizontal_flip(self):
        image = np.random.rand(640, 480, 3)
        mask = np.random.rand(640, 480)
        joints = np.random.randint(0, 100, size=(1, 17, 3))

        aug = KeypointsRandomHorizontalFlip(flip_index=[16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], prob=1)
        aug_image, aug_mask, aug_joints = aug(image, mask, joints)

        np.testing.assert_array_equal(aug_image, image[:, ::-1, :])
        np.testing.assert_array_equal(aug_mask, mask[:, ::-1])
        np.testing.assert_array_equal(image.shape[1] - aug_joints[:, ::-1, 0] - 1, joints[..., 0])
        np.testing.assert_array_equal(aug_joints[:, ::-1, 1], joints[..., 1])
        np.testing.assert_array_equal(aug_joints[:, ::-1, 2], joints[..., 2])

    def test_keypoints_vertical_flip(self):
        image = np.random.rand(640, 480, 3)
        mask = np.random.rand(640, 480)
        joints = np.random.randint(0, 100, size=(1, 17, 3))

        aug = KeypointsRandomVerticalFlip(prob=1)
        aug_image, aug_mask, aug_joints = aug(image, mask, joints)

        np.testing.assert_array_equal(aug_image, image[::-1, :, :])
        np.testing.assert_array_equal(aug_mask, mask[::-1, :])
        np.testing.assert_array_equal(aug_joints[..., 0], joints[..., 0])
        np.testing.assert_array_equal(image.shape[0] - aug_joints[..., 1] - 1, joints[..., 1])
        np.testing.assert_array_equal(aug_joints[..., 2], joints[..., 2])

    def test_keypoints_pad_if_needed(self):
        image = np.random.rand(640, 480, 3)
        mask = np.random.rand(640, 480)
        joints = np.random.randint(0, 100, size=(1, 17, 3))

        aug = KeypointsPadIfNeeded(min_width=768, min_height=768, image_pad_value=0, mask_pad_value=0)
        aug_image, aug_mask, aug_joints = aug(image, mask, joints)

        self.assertEqual(aug_image.shape, (768, 768, 3))
        self.assertEqual(aug_mask.shape, (768, 768))
        np.testing.assert_array_equal(aug_joints, joints)

    def test_keypoints_longest_max_size(self):
        image = np.random.rand(640, 480, 3)
        mask = np.random.rand(640, 480)
        joints = np.random.randint(0, 480, size=(1, 17, 3))

        aug = KeypointsLongestMaxSize(max_height=512, max_width=512)
        aug_image, aug_mask, aug_joints = aug(image, mask, joints)

        self.assertEqual(aug_image.shape[:2], aug_mask.shape[:2])
        self.assertLessEqual(aug_image.shape[0], 512)
        self.assertLessEqual(aug_image.shape[1], 512)

        self.assertTrue((aug_joints[..., 0] < aug_image.shape[1]).all())
        self.assertTrue((aug_joints[..., 1] < aug_image.shape[0]).all())


if __name__ == "__main__":
    unittest.main()
