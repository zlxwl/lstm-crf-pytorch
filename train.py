from model import *
from utils import *
from evaluate import *

def load_data(hre):
    hre_size = 0 # size of HRE block
    bxc = [] # character sequence batch
    bxw = [] # word sequence batch
    by = [[]] if hre else [] # label batch
    data = []
    cti = load_tkn_to_idx(sys.argv[2]) # char_to_idx
    wti = load_tkn_to_idx(sys.argv[3]) # word_to_idx
    itt = load_idx_to_tkn(sys.argv[4]) # idx_to_tkn
    print("loading %s..." % sys.argv[5])
    fo = open(sys.argv[5], "r")
    for line in fo:
        line = line.strip()
        if line:
            seq = line.split(" ")
            y = int(seq.pop()) if hre else [int(i) for i in seq[len(seq) // 2:]]
            x = [i.split(":") for i in (seq if hre else seq[:len(seq) // 2])]
            xc, xw = zip(*[(list(map(int, xc.split("+"))), int(xw)) for xc, xw in x])
            bxc.append(xc)
            bxw.append(xw)
            (by[-1] if hre else by).append(y)
        elif hre: # empty line as block delimiter
            if hre_size == 0:
                hre_size = len(by[-1])
            by[-1] += [PAD_IDX] * (hre_size - len(by[-1]))
            by.append([])
        if len(by) == BATCH_SIZE:
            bxc, bxw = batchify(bxc, bxw)
            _, by = batchify(None, by, sos = True)
            data.append((bxc, bxw, by))
            bxc = []
            bxw = []
            by = [[]] if hre else []
    fo.close()
    print("data size: %d" % (len(data) * BATCH_SIZE))
    print("batch size: %d" % BATCH_SIZE)
    return data, cti, wti, itt

def train():
    hre = (UNIT == "sent") # hierarchical recurrent encoding (HRE)
    num_epochs = int(sys.argv[-1])
    data, cti, wti, itt = load_data(hre)
    model = rnn_crf(len(cti), len(wti), len(itt), hre)
    optim = torch.optim.Adam(model.parameters(), lr = LEARNING_RATE)
    print(model)
    epoch = load_checkpoint(sys.argv[1], model) if isfile(sys.argv[1]) else 0
    filename = re.sub("\.epoch[0-9]+$", "", sys.argv[1])
    print("training model...")
    for ei in range(epoch + 1, epoch + num_epochs + 1):
        loss_sum = 0
        timer = time()
        for xc, xw, y in data:
            loss = model(xc, xw, y) # forward pass and compute loss
            loss.backward() # compute gradients
            optim.step() # update parameters
            loss_sum += loss.item()
        timer = time() - timer
        loss_sum /= len(data)
        if ei % SAVE_EVERY and ei != epoch + num_epochs:
            save_checkpoint("", None, ei, loss_sum, timer)
        else:
            save_checkpoint(filename, model, ei, loss_sum, timer)
        if EVAL_EVERY and (ei % EVAL_EVERY == 0 or ei == epoch + num_epochs):
            args = [model, cti, wti, itt]
            evaluate(predict(sys.argv[-1], *args), True)
            model.train()
            print()

if __name__ == "__main__":
    if len(sys.argv) not in [7, 8]:
        sys.exit("Usage: %s model char_to_idx word_to_idx tag_to_idx training_data (validation_data) num_epoch" % sys.argv[0])
    print("cuda: %s" % CUDA)
    train()
