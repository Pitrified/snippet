from matplotlib import pyplot as plt  # type: ignore
import numpy as np
import streamlit as st


class AlignApp:
    def __init__(self):
        """"""
        self.rng = np.random.default_rng(12345)
        self.num_en = 50
        self.num_fr = 70
        self.ratio_fren = self.num_fr / self.num_en
        self.sent_win = 4

        self.sents_en = [f"en {i}" for i in range(self.num_en)]
        self.sents_fr = [f"fr {i}" for i in range(self.num_fr)]

        self.title = st.title("Develop UI")
        self.title_side = st.sidebar.title("Develop UI")

        self.create_fake_alignment()
        self.check_ooo()

        fig, ax = plt.subplots()
        ax.plot(self.ids_en, self.ids_fr)
        st.pyplot(fig)

        # the index of the first ooo, in the sentences we see
        self.first_ooo_id = self.is_ooo.index(True)
        st.write(f"{self.first_ooo_id=}")

        # find the index of the en sentence in the whole list of sentences
        self.full_id_en = self.ids_en[self.first_ooo_id]
        st.write(f"{self.full_id_en=}")

        # index of the fr sentence in the whole list of sentences
        self.full_id_fr_ratio = int(self.full_id_en * self.ratio_fren)
        st.write(f"{self.full_id_fr_ratio=}")

        # mismatched fr sent index
        self.full_id_fr_miss = self.ids_fr[self.first_ooo_id]
        st.write(f"{self.full_id_fr_miss=}")

        # now show a bunch of en sents centered on full_id_en
        # and show a bunch of fr sents centered on full_id_fr_miss
        # and a bunch of buttons to pick the right fr sentence matching full_id_en
        # then save the correct match in the session state
        # next time the program is run you have to read the session state and reload the fixes
        # the problem is that every time the program runs the epubs are reloaded
        #     which takes 5-10 seconds...
        # would need to find a way to avoid the nlp part of the load the second time
        # just set a flag in the state bruh
        # have to do the same thing as Optional[pipeline] we did for huggingface

        # find a way to unload the translation model and then load the sentence model
        # and the whole thing could even run in the sad GPU we have

        # or we could show the eng sentences (all the mismatched one)
        # and use a slider to match with the right french one
        # so we can use the sliders as memory lmao no I hate this

        # self.en_slide = st.slider("Id en", 0, len(self.ids_en), value=self.first_ooo_id)
        # self.en_curr_id = st.text(f"Current en id {self.en_slide}")
        # st.write(type(self.en_slide))

        self.cols_sent = st.columns(3)

        # for iz, z in enumerate(zip(self.ids_en, self.ids_fr, self.is_ooo)):
        #     if iz - self.sent_win < self.en_slide < iz + self.sent_win:
        #         self.cols_sent[0].write(z[0])
        #         self.cols_sent[1].write(z[1])
        #         self.cols_sent[2].button(
        #             f"{self.ids_en[self.en_slide]} to {z[1]}",
        #             key=f"match_{self.en_slide}_{z[0]}_{z[1]}",
        #         )

    def create_fake_alignment(self):
        """"""
        self.ids_en = []
        self.ids_fr = []

        for ei in range(self.num_en):
            prob_add = self.rng.random()
            if prob_add < 0.8:
                fi = int(ei * self.ratio_fren)
                err_align = self.rng.integers(0, self.rng.integers(1, 5))
                self.ids_en.append(ei)
                self.ids_fr.append(fi + err_align)

    def check_ooo(self):
        """"""

        self.is_ooo = []

        for j, (id_en, id_fr) in enumerate(zip(self.ids_en, self.ids_fr)):

            # check for out of order ids
            ooo = False

            if j == 0:
                # only check to the right for the first value
                if id_fr > self.ids_fr[j + 1]:
                    ooo = True
            elif j == len(self.ids_fr) - 1:
                # only check to the left for the last value
                if id_fr < self.ids_fr[j - 1]:
                    ooo = True
            else:
                if id_fr > self.ids_fr[j + 1] or id_fr < self.ids_fr[j - 1]:
                    ooo = True

            if ooo:
                print(j, id_en, id_fr)

            self.is_ooo.append(ooo)


def main() -> None:
    """"""
    a = AlignApp()


if __name__ == "__main__":
    main()
