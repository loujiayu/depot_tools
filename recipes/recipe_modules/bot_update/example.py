# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPS = [
  'bot_update',
  'gclient',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
]

def RunSteps(api):
  api.gclient.use_mirror = True

  src_cfg = api.gclient.make_config(CACHE_DIR='[GIT_CACHE]')
  soln = src_cfg.solutions.add()
  soln.name = 'src'
  soln.url = 'https://chromium.googlesource.com/chromium/src.git'
  soln.revision = api.properties.get('revision')
  api.gclient.c = src_cfg
  api.gclient.c.revisions.update(api.properties.get('revisions', {}))
  api.gclient.c.got_revision_mapping['src'] = 'got_cr_revision'
  api.gclient.c.patch_projects['v8'] = ('src/v8', 'HEAD')
  api.gclient.c.patch_projects['angle/angle'] = ('src/third_party/angle',
                                                 'HEAD')
  patch = api.properties.get('patch', True)
  clobber = True if api.properties.get('clobber') else False
  no_shallow = True if api.properties.get('no_shallow') else False
  output_manifest = api.properties.get('output_manifest', False)
  with_branch_heads = api.properties.get('with_branch_heads', False)
  with_tags = api.properties.get('with_tags', False)
  refs = api.properties.get('refs', [])
  oauth2 = api.properties.get('oauth2', False)
  oauth2_json = api.properties.get('oauth2_json', False)
  root_solution_revision = api.properties.get('root_solution_revision')
  suffix = api.properties.get('suffix')
  gerrit_no_reset = True if api.properties.get('gerrit_no_reset') else False
  gerrit_no_rebase_patch_ref = bool(
      api.properties.get('gerrit_no_rebase_patch_ref'))

  if api.properties.get('test_apply_gerrit_ref'):
    api.bot_update.apply_gerrit_ref(
        root='/tmp/test/root',
        gerrit_no_reset=gerrit_no_reset,
        gerrit_no_rebase_patch_ref=gerrit_no_rebase_patch_ref)
  else:
    bot_update_step = api.bot_update.ensure_checkout(
        no_shallow=no_shallow,
        patch=patch,
        with_branch_heads=with_branch_heads,
        with_tags=with_tags,
        output_manifest=output_manifest,
        refs=refs, patch_oauth2=oauth2,
        oauth2_json=oauth2_json,
        clobber=clobber,
        root_solution_revision=root_solution_revision,
        suffix=suffix,
        gerrit_no_reset=gerrit_no_reset,
        gerrit_no_rebase_patch_ref=gerrit_no_rebase_patch_ref)
    if patch:
      api.bot_update.deapply_patch(bot_update_step)


def GenTests(api):
  yield api.test('basic') + api.properties(
      patch=False,
      revision='abc'
  )
  yield api.test('buildbot') + api.properties(
      path_config='buildbot',
      patch=False,
      revision='abc'
  )
  yield api.test('basic_with_branch_heads') + api.properties(
      with_branch_heads=True,
      suffix='with branch heads'
  )
  yield api.test('basic_output_manifest') + api.properties(
      output_manifest=True,
  )
  yield api.test('with_tags') + api.properties(with_tags=True)
  yield api.test('tryjob') + api.properties(
      issue=12345,
      patchset=654321,
      rietveld='https://rietveld.example.com/',
  )
  yield api.test('trychange') + api.properties(
      refs=['+refs/change/1/2/333'],
  )
  yield api.test('trychange_oauth2') + api.properties(
      oauth2=True,
  )
  yield api.test('trychange_oauth2_buildbot') + api.properties(
      path_config='buildbot',
      oauth2=True,
  )
  yield api.test('trychange_oauth2_json') + api.properties(
      mastername='tryserver.chromium.linux',
      buildername='linux_rel',
      slavename='totallyaslave-c4',
      oauth2_json=True,
  )
  yield api.test('trychange_oauth2_json_win') + api.properties(
      mastername='tryserver.chromium.win',
      buildername='win_rel',
      slavename='totallyaslave-c4',
      oauth2_json=True,
  ) + api.platform('win', 64)
  yield api.test('tryjob_fail') + api.properties(
      issue=12345,
      patchset=654321,
      rietveld='https://rietveld.example.com/',
  ) + api.step_data('bot_update', retcode=1)
  yield api.test('tryjob_fail_patch') + api.properties(
      issue=12345,
      patchset=654321,
      rietveld='https://rietveld.example.com/',
      fail_patch='apply',
  ) + api.step_data('bot_update', retcode=88)
  yield api.test('tryjob_fail_patch_download') + api.properties(
      issue=12345,
      patchset=654321,
      rietveld='https://rietveld.example.com/',
      fail_patch='download'
  ) + api.step_data('bot_update', retcode=87)
  yield api.test('no_shallow') + api.properties(
      no_shallow=1
  )
  yield api.test('clobber') + api.properties(
      clobber=1
  )
  yield api.test('reset_root_solution_revision') + api.properties(
      root_solution_revision='revision',
  )
  yield api.test('gerrit_no_reset') + api.properties(
      gerrit_no_reset=1
  )
  yield api.test('gerrit_no_rebase_patch_ref') + api.properties(
      gerrit_no_rebase_patch_ref=True
  )
  yield api.test('apply_gerrit_ref') + api.properties(
      repository='chromium',
      gerrit_no_rebase_patch_ref=True,
      gerrit_no_reset=1,
      test_apply_gerrit_ref=True,
  )
  yield api.test('tryjob_v8') + api.properties(
      issue=12345,
      patchset=654321,
      rietveld='https://rietveld.example.com/',
      patch_project='v8',
      revisions={'src/v8': 'abc'}
  )
  yield api.test('tryjob_v8_head_by_default') + api.properties.tryserver(
      patch_project='v8',
  )
  yield api.test('tryjob_gerrit_angle') + api.properties.tryserver(
      gerrit_project='angle/angle',
      patch_issue=338811,
      patch_set=3,
  )
  yield api.test('tryjob_gerrit_angle_deprecated') + api.properties.tryserver(
      patch_project='angle/angle',
      gerrit='https://chromium-review.googlesource.com',
      patch_storage='gerrit',
      repository='https://chromium.googlesource.com/angle/angle',
      rietveld=None,
      **{
        'event.change.id': 'angle%2Fangle~master~Ideadbeaf',
        'event.change.number': 338811,
        'event.change.url':
          'https://chromium-review.googlesource.com/#/c/338811',
        'event.patchSet.ref': 'refs/changes/11/338811/3',
      }
  )
