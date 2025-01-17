import random
from itertools import product
import os.path
from abcvoting import genprofiles
from abcvoting.misc import check_enough_approved_candidates
from operator import itemgetter
from abcvoting import abcrules
from abcvoting import fileio


def generate_profile(num_voters, num_cand, committeesize, prob_distribution, setsize):
    while True:
        if prob_distribution == "IC":
            profile = genprofiles.random_IC_profile(num_cand, num_voters, setsize)
        elif prob_distribution.startswith("Mallows"):
            dispersion = float(prob_distribution[7:])
            profile = genprofiles.random_mallows_profile(
                num_cand, num_voters, setsize, dispersion=dispersion
            )
        elif prob_distribution.startswith("Urn"):
            replace = float(prob_distribution[3:])
            profile = genprofiles.random_urn_profile(
                num_cand, num_voters, setsize, replace=replace
            )
        elif prob_distribution == "IC-party":
            profile = genprofiles.random_IC_party_list_profile(num_cand, num_voters, num_parties=3)
        else:
            raise ValueError
        try:
            check_enough_approved_candidates(profile, committeesize)
            return profile
        except ValueError:
            pass


def generate_abc_yaml_testinstances(
    batchname,
    committeesizes,
    num_voters_values,
    num_cand_values,
    prob_distributions,
    approval_setsizes,
    av_neq_pav=False,
):
    random.seed(24121838)

    parameter_tuples = []
    for committeesize, num_voters, num_cand, prob_distribution, setsize in product(
        committeesizes, num_voters_values, num_cand_values, prob_distributions, approval_setsizes
    ):
        if committeesize >= num_cand:
            continue
        if setsize == "committeesize":
            setsize = committeesize
        parameter_tuples.append((committeesize, num_voters, num_cand, prob_distribution, setsize))
    parameter_tuples.sort(key=itemgetter(2))

    print(f"Generating {len(parameter_tuples)} instances for batch {batchname}...")
    num_instances = 0

    for index, (committeesize, num_voters, num_cand, prob_distribution, setsize) in enumerate(
        parameter_tuples
    ):
        num_instances += 1

        # write instance to .abc.yaml file
        currdir = os.path.dirname(os.path.abspath(__file__))
        filename = currdir + f"/instance{batchname}{index:04d}.abc.yaml"

        print(f"generating {filename} ({prob_distribution})")
        while True:
            profile = generate_profile(
                num_voters, num_cand, committeesize, prob_distribution, setsize
            )
            committees_av = abcrules.compute("av", profile, committeesize, resolute=False)
            committees_pav = abcrules.compute("pav", profile, committeesize, resolute=False)
            if not av_neq_pav:
                break
            intersection = set(tuple(sorted(committee)) for committee in committees_pav) & set(
                tuple(sorted(committee)) for committee in committees_av
            )
            if not intersection:
                break

        rule_instances = []
        for rule_id in abcrules.MAIN_RULE_IDS:
            rule = abcrules.get_rule(rule_id)
            # if rule_id == "minimaxphragmen":
            #     algorithm = "mip_gurobi"
            # else:
            #     algorithm = "fastest"

            # if irresolute (resolute = False) is supported, then "expected_committees" should be
            # the list of committees returned for resolute=False.
            if False in rule.resolute_values:
                resolute = False
            else:
                resolute = True
            committees = abcrules.compute(rule_id, profile, committeesize, resolute=resolute)

            for resolute in rule.resolute_values:
                rule_instances.append(
                    {"rule_id": rule_id, "resolute": resolute, "expected_committees": committees}
                )

        fileio.write_abcvoting_instance_to_yaml_file(
            filename,
            profile,
            committeesize=committeesize,
            description=(
                f"profile generated via prob_distribution={prob_distribution}, "
                f"num_voters={num_voters}, "
                f"num_cand={num_cand}, "
                f"setsize={setsize}"
            ),
            compute_instances=rule_instances,
        )

    print("Done.")


if __name__ == "__main__":
    batch = "S"
    committeesizes = [3, 4]
    num_voters_values = [8, 9]
    num_cand_values = [6]
    prob_distributions = ["IC"]
    approval_setsizes = [3]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=True,
    )

    batch = "M"
    committeesizes = [3, 4]
    num_voters_values = [8, 9, 10, 11]
    num_cand_values = [6, 7]
    prob_distributions = ["IC"]
    approval_setsizes = [2, 3]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=True,
    )

    batch = "L"
    committeesizes = [3, 4, 5, 6]
    num_voters_values = [8, 12, 15]
    num_cand_values = [6, 8, 9]
    prob_distributions = ["IC", "Mallows0.8", "Urn0.5"]
    approval_setsizes = [2, 3]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=False,
    )

    batch = "Mallow"
    committeesizes = [5, 6]
    num_voters_values = [13, 16]
    num_cand_values = [8, 9]
    prob_distributions = ["Mallows0.2", "Mallows0.5", "Mallows0.8"]
    approval_setsizes = [2, 3, 4]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=False,
    )

    batch = "P"
    committeesizes = [3, 4, 5]
    num_voters_values = [12, 15]
    num_cand_values = [5, 6]
    prob_distributions = ["IC-party"]
    approval_setsizes = [None]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=False,
    )

    batch = "VL"
    committeesizes = [6]
    num_voters_values = [24, 25]
    num_cand_values = [8, 9]
    prob_distributions = ["IC", "Mallows0.5", "Mallows0.8", "Urn0.5"]
    approval_setsizes = [2, 3, 5]
    generate_abc_yaml_testinstances(
        batch,
        committeesizes,
        num_voters_values,
        num_cand_values,
        prob_distributions,
        approval_setsizes,
        av_neq_pav=False,
    )
